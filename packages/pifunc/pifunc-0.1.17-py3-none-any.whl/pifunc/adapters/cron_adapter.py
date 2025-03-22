# pifunc/adapters/cron_adapter.py - partial fix for the tags issue
import time
import threading
import logging
import inspect
import datetime
from typing import Any, Callable, Dict, List, Optional
from pifunc.adapters import ProtocolAdapter

logger = logging.getLogger(__name__)

# Try to import schedule library safely
try:
    import schedule

    _schedule_available = True
except ImportError:
    _schedule_available = False
    print("Warning: Schedule library not available. CRON adapter will be disabled.")


class CRONAdapter(ProtocolAdapter):
    """Adapter dla zadań cyklicznych (CRON)."""

    def __init__(self):
        self.config = {}
        self.jobs = {}
        self._running = False
        self._scheduler_thread = None
        self._clients = {}
        self._connected = _schedule_available

    def setup(self, config: Dict[str, Any]) -> None:
        """Konfiguruje adapter CRON."""
        self.config = config
        # Add force connection flag
        self.force_connection = config.get("force_connection", False)

        if not _schedule_available:
            if self.force_connection:
                raise ImportError("Schedule library is required but not available.")
            self._connected = False
            return

        # Konfiguracja domyślnych interwałów
        self.default_interval = config.get("default_interval", "1m")
        self.check_interval = config.get("check_interval", 1)  # Sekundy

        # Klienci dla wywoływania innych usług
        if "clients" in config:
            self._clients = config["clients"]

    def register_function(self, func: Callable, metadata: Dict[str, Any]) -> None:
        """Rejestruje funkcję jako zadanie CRON."""
        if not self._connected:
            logger.warning(f"CRON adapter not available, skipping registration of {func.__name__}")
            return

        # Pobieramy konfigurację CRON
        cron_config = metadata.get("cron", {})

        if not cron_config and not metadata.get("_is_client_function", False):
            logger.warning(
                f"Funkcja {func.__name__} nie zawiera konfiguracji CRON, ale jest rejestrowana w adapterze CRON")
            print(f"Funkcja {func.__name__} nie zawiera konfiguracji CRON, ale jest rejestrowana w adapterze CRON")
            return

        # Przygotowujemy konfigurację zadania
        job_config = {
            "function": func,
            "metadata": metadata,
            "schedule": self._parse_schedule(cron_config),
            "last_run": None,
            "next_run": None,
            "enabled": cron_config.get("enabled", True),
            "tags": cron_config.get("tags", []),
            "description": cron_config.get("description", func.__doc__ or ""),
            "timeout": cron_config.get("timeout", 300),  # 5 minut
            "max_retries": cron_config.get("max_retries", 3),
            "retry_delay": cron_config.get("retry_delay", 60),  # 1 minuta
            "client_config": metadata.get("client", {})
        }

        # Dodajemy zadanie do listy
        self.jobs[func.__name__] = job_config

        logger.info(f"Zarejestrowano zadanie CRON: {func.__name__}")

    def _parse_interval(self, interval: str) -> Any:
        """Parsuje interwał w formacie 'XyXdXhXmXs'."""
        if not self._connected:
            return None

        # Obsługujemy różne formaty
        if not interval:
            # Domyślnie 1 minuta
            return schedule.every(1).minutes

        # Sprawdzamy, czy to prosty format
        if interval.endswith('s'):
            seconds = int(interval[:-1])
            return schedule.every(seconds).seconds
        elif interval.endswith('m'):
            minutes = int(interval[:-1])
            return schedule.every(minutes).minutes
        elif interval.endswith('h'):
            hours = int(interval[:-1])
            return schedule.every(hours).hours
        elif interval.endswith('d'):
            days = int(interval[:-1])
            return schedule.every(days).days
        elif interval.endswith('w'):
            weeks = int(interval[:-1])
            return schedule.every(weeks).weeks

        # Złożony format (np. "1h30m")
        total_seconds = 0
        current_number = ""

        for char in interval:
            if char.isdigit():
                current_number += char
            elif char == 'y' and current_number:
                total_seconds += int(current_number) * 365 * 24 * 3600
                current_number = ""
            elif char == 'd' and current_number:
                total_seconds += int(current_number) * 24 * 3600
                current_number = ""
            elif char == 'h' and current_number:
                total_seconds += int(current_number) * 3600
                current_number = ""
            elif char == 'm' and current_number:
                total_seconds += int(current_number) * 60
                current_number = ""
            elif char == 's' and current_number:
                total_seconds += int(current_number)
                current_number = ""

        if total_seconds == 0:
            try:
                # Próbujemy zinterpretować jako liczbę sekund
                total_seconds = int(interval)
            except ValueError:
                # Używamy domyślnej wartości 1 minuty
                total_seconds = 60

        return schedule.every(total_seconds).seconds

    def _execute_job(self, job_name: str) -> None:
        """Wykonuje zadanie CRON."""
        if not self._connected:
            return

        if job_name not in self.jobs:
            logger.error(f"Nieznane zadanie: {job_name}")
            return

        job_config = self.jobs[job_name]

        if not job_config["enabled"]:
            logger.debug(f"Zadanie {job_name} jest wyłączone")
            return

        func = job_config["function"]
        retry_count = 0

        # Aktualizujemy informacje o ostatnim uruchomieniu
        job_config["last_run"] = datetime.datetime.now()

        logger.info(f"Uruchamianie zadania CRON: {job_name}")

        # Wykonujemy zadanie z obsługą błędów i ponowień
        while retry_count <= job_config["max_retries"]:
            try:
                # Sprawdzamy, czy to funkcja kliencka
                if job_config["client_config"]:
                    self._execute_client_function(func, job_config["client_config"])
                else:
                    # Standardowe wywołanie funkcji
                    result = func()

                    # Logujemy wynik
                    logger.info(f"Zadanie {job_name} zakończone: {result}")

                # Sukces, przerywamy pętle
                break
            except Exception as e:
                retry_count += 1
                logger.error(
                    f"Błąd wykonania zadania {job_name} (próba {retry_count}/{job_config['max_retries']}): {str(e)}")

                if retry_count <= job_config["max_retries"]:
                    # Czekamy przed ponowieniem
                    time.sleep(job_config["retry_delay"])
                else:
                    logger.error(f"Zadanie {job_name} nie powiodło się po {retry_count} próbach")

    def _execute_client_function(self, func: Callable, client_config: Dict[str, Any]) -> Any:
        """Wykonuje funkcję kliencką, która wywołuje inną usługę."""
        if not self._connected:
            return None

        # Pobieramy konfigurację klienta
        protocol = client_config.get("protocol", "http")

        # Sprawdzamy, czy mamy klienta dla tego protokołu
        if protocol not in self._clients:
            raise ValueError(f"Brak klienta dla protokołu: {protocol}")

        client = self._clients[protocol]

        # Przygotowujemy argumenty dla klienta
        # Wywołujemy funkcję, aby uzyskać dane
        data = func()

        # Wywołujemy klienta z odpowiednimi parametrami
        target_service = client_config.get("service", func.__name__)

        # Dodatkowe parametry dla klienta
        extra_params = {}
        for key, value in client_config.items():
            if key not in ["protocol", "service"]:
                extra_params[key] = value

        # Wywołujemy usługę docelową
        return client.call(target_service, data, **extra_params)

    def _parse_schedule(self, cron_config: Dict[str, Any]) -> Any:
        """Parsuje konfigurację harmonogramu z różnych formatów."""
        if not self._connected:
            return None

        # Możemy obsługiwać wiele formatów

        # 1. Klasyczna składnia CRON (np. "* * * * *")
        if "cron_expression" in cron_config:
            expr = cron_config["cron_expression"]
            # Konwertujemy do formatu schedule
            minute, hour, day, month, day_of_week = expr.split()

            job = schedule.Schedule()

            # Logika parsowania wyrażenia CRON i ustawiania schedule
            # Uwaga: To jest uproszczona wersja, pełny parser byłby bardziej złożony
            if minute != "*":
                job = job.at(f"{hour.zfill(2)}:{minute.zfill(2)}")

            if day_of_week != "*":
                days = {
                    "0": "sunday", "1": "monday", "2": "tuesday",
                    "3": "wednesday", "4": "thursday", "5": "friday", "6": "saturday"
                }
                job = getattr(job, days.get(day_of_week, "every().day"))()

            return job

        # 2. Interwał (np. "10m", "1h", "30s")
        elif "interval" in cron_config:
            interval = cron_config["interval"]
            return self._parse_interval(interval)

        # 3. Konkretny czas (np. "12:00", "18:30")
        elif "at" in cron_config:
            at_time = cron_config["at"]
            return schedule.every().day.at(at_time)

        # 4. Dzień tygodnia z czasem (np. "monday", "friday at 18:00")
        elif any(day in cron_config for day in
                 ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]):
            for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
                if day in cron_config:
                    time_spec = cron_config[day]
                    if isinstance(time_spec, str) and "at" in time_spec:
                        at_time = time_spec.split("at")[1].strip()
                        return getattr(schedule.every(), day).at(at_time)
                    else:
                        return getattr(schedule.every(), day)

        # Domyślny harmonogram
        return self._parse_interval(self.default_interval)

    def _scheduler_loop(self) -> None:
        """Główna pętla planisty."""
        if not self._connected:
            return

        while self._running:
            try:
                # Uruchamiamy zaplanowane zadania
                schedule.run_pending()

                # Aktualizujemy informacje o następnym uruchomieniu dla każdego zadania
                for job_name, job_config in self.jobs.items():
                    # Planujemy zadanie, jeśli jeszcze nie jest zaplanowane
                    scheduled_jobs = set()

                    # Extract tags from all jobs safely
                    for job in schedule.jobs:
                        # Ensure every job has a tags attribute
                        if not hasattr(job, 'tags'):
                            setattr(job, 'tags', [])

                        # Convert any type to list for consistency
                        if not isinstance(job.tags, list):
                            if isinstance(job.tags, (tuple, set)):
                                job.tags = list(job.tags)
                            elif job.tags is not None:
                                job.tags = [job.tags]
                            else:
                                job.tags = []

                        # Add all tags from this job
                        scheduled_jobs.update(job.tags)

                    if job_name not in scheduled_jobs:
                        # Dodajemy zadanie do harmonogramu
                        job = job_config["schedule"].do(self._execute_job, job_name)

                        # Ensure tags is a list and add the job name as a tag
                        if not hasattr(job, 'tags'):
                            job.tags = []
                        elif not isinstance(job.tags, list):
                            job.tags = list(job.tags) if job.tags else []

                        # Add job_name as a tag if needed
                        if job_name not in job.tags:
                            job.tags.append(job_name)

                        # Make sure the job has a tag method
                        if not hasattr(job, 'tag'):
                            def tag_method(self, tag_name):
                                if not hasattr(self, 'tags'):
                                    self.tags = []
                                if tag_name not in self.tags:
                                    self.tags.append(tag_name)
                                return self

                            # Bind the method to the job
                            from types import MethodType
                            job.tag = MethodType(tag_method, job)

                    # Aktualizujemy informację o następnym uruchomieniu
                    for scheduled_job in schedule.jobs:
                        # Safely access tags
                        tags = getattr(scheduled_job, 'tags', [])
                        if isinstance(tags, (list, tuple)) and job_name in tags:
                            job_config["next_run"] = scheduled_job.next_run
                            break
                        elif isinstance(tags, set) and job_name in tags:
                            job_config["next_run"] = scheduled_job.next_run
                            break

                # Czekamy przed następnym sprawdzeniem
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(self.check_interval)

    def start(self) -> None:
        """Uruchamia adapter CRON."""
        if self._running or not self._connected:
            logger.warning("CRON adapter is already running or not connected")
            return

        # Czyszczenie istniejących zadań
        if hasattr(schedule, 'clear'):
            schedule.clear()

        # Ustawiamy flagę uruchomienia
        self._running = True

        # Uruchamiamy pętlę planisty w osobnym wątku
        self._scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self._scheduler_thread.start()

        logger.info("CRON adapter started")
        print("Adapter CRON uruchomiony")

    def stop(self) -> None:
        """Zatrzymuje adapter CRON."""
        if not self._running or not self._connected:
            return

        # Zatrzymujemy pętlę planisty
        self._running = False

        # Czekamy na zakończenie wątku
        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=5.0)

        # Czyszczenie zadań
        if hasattr(schedule, 'clear'):
            schedule.clear()

        logger.info("CRON adapter stopped")
        print("Adapter CRON zatrzymany")

    def list_jobs(self) -> List[Dict[str, Any]]:
        """Zwraca listę wszystkich zarejestrowanych zadań."""
        if not self._connected:
            return []

        result = []

        for job_name, job_config in self.jobs.items():
            job_info = {
                "name": job_name,
                "enabled": job_config["enabled"],
                "description": job_config["description"],
                "tags": job_config["tags"],
                "last_run": job_config["last_run"],
                "next_run": job_config["next_run"]
            }

            result.append(job_info)

        return result

    def enable_job(self, job_name: str) -> bool:
        """Włącza zadanie."""
        if not self._connected:
            return False

        if job_name in self.jobs:
            self.jobs[job_name]["enabled"] = True
            return True
        return False

    def disable_job(self, job_name: str) -> bool:
        """Wyłącza zadanie."""
        if not self._connected:
            return False

        if job_name in self.jobs:
            self.jobs[job_name]["enabled"] = False
            return True
        return False

    def run_job_now(self, job_name: str) -> bool:
        """Uruchamia zadanie natychmiast."""
        if not self._connected:
            return False

        if job_name in self.jobs:
            self._execute_job(job_name)
            return True
        return False