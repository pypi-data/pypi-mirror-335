# pifunc/adapters/cron_adapter.py
import time
import threading
import logging
import schedule
import inspect
import datetime
from typing import Any, Callable, Dict, List, Optional
from pifunc.adapters import ProtocolAdapter

logger = logging.getLogger(__name__)


class CRONAdapter(ProtocolAdapter):
    """Adapter dla zadań cyklicznych (CRON)."""

    def __init__(self):
        self.config = {}
        self.jobs = {}
        self._running = False
        self._scheduler_thread = None
        self._clients = {}

    def setup(self, config: Dict[str, Any]) -> None:
        """Konfiguruje adapter CRON."""
        self.config = config

        # Konfiguracja domyślnych interwałów
        self.default_interval = config.get("default_interval", "1m")
        self.check_interval = config.get("check_interval", 1)  # Sekundy

        # Klienci dla wywoływania innych usług
        if "clients" in config:
            self._clients = config["clients"]

    def register_function(self, func: Callable, metadata: Dict[str, Any]) -> None:
        """Rejestruje funkcję jako zadanie CRON."""
        # Pobieramy konfigurację CRON
        cron_config = metadata.get("cron", {})

        if not cron_config and not metadata.get("_is_client_function", False):
            logger.warning(
                f"Funkcja {func.__name__} nie zawiera konfiguracji CRON, ale jest rejestrowana w adapterze CRON")
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

    def _parse_schedule(self, cron_config: Dict[str, Any]) -> Any:
        """Parsuje konfigurację harmonogramu z różnych formatów."""
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

    def _parse_interval(self, interval: str) -> Any:
        """Parsuje interwał w formacie 'XyXdXhXmXs'."""
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

    def _scheduler_loop(self) -> None:
        """Główna pętla planisty."""
        while self._running:
            # Uruchamiamy zaplanowane zadania
            schedule.run_pending()

            # Aktualizujemy informacje o następnym uruchomieniu dla każdego zadania
            for job_name, job_config in self.jobs.items():
                # Planujemy zadanie, jeśli jeszcze nie jest zaplanowane
                if job_name not in [job.tags[0] for job in schedule.jobs]:
                    # Dodajemy zadanie do harmonogramu
                    job = job_config["schedule"].do(self._execute_job, job_name)
                    job.tag(job_name)

                # Aktualizujemy informację o następnym uruchomieniu
                for scheduled_job in schedule.jobs:
                    if job_name in scheduled_job.tags:
                        job_config["next_run"] = scheduled_job.next_run
                        break

            # Czekamy przed następnym sprawdzeniem
            time.sleep(self.check_interval)

    def start(self) -> None:
        """Uruchamia adapter CRON."""
        if self._running:
            logger.warning("Adapter CRON jest już uruchomiony")
            return

        # Czyszczenie istniejących zadań
        schedule.clear()

        # Ustawiamy flagę uruchomienia
        self._running = True

        # Uruchamiamy pętlę planisty w osobnym wątku
        self._scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self._scheduler_thread.start()

        logger.info("Adapter CRON uruchomiony")

    def stop(self) -> None:
        """Zatrzymuje adapter CRON."""
        if not self._running:
            return

        # Zatrzymujemy pętlę planisty
        self._running = False

        # Czekamy na zakończenie wątku
        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=5.0)

        # Czyszczenie zadań
        schedule.clear()

        logger.info("Adapter CRON zatrzymany")

    def list_jobs(self) -> List[Dict[str, Any]]:
        """Zwraca listę wszystkich zarejestrowanych zadań."""
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
        if job_name in self.jobs:
            self.jobs[job_name]["enabled"] = True
            return True
        return False

    def disable_job(self, job_name: str) -> bool:
        """Wyłącza zadanie."""
        if job_name in self.jobs:
            self.jobs[job_name]["enabled"] = False
            return True
        return False

    def run_job_now(self, job_name: str) -> bool:
        """Uruchamia zadanie natychmiast."""
        if job_name in self.jobs:
            self._execute_job(job_name)
            return True
        return False