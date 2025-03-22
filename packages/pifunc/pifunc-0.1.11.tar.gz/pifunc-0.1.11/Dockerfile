FROM python:3.11-slim

WORKDIR /app

# Copy the entire project including src directory
COPY . .

# Install local pifunc package in development mode
RUN pip install -e .

# Install other dependencies
RUN pip install --no-cache-dir -r calculator/requirements.txt

# Expose ports for HTTP and WebSocket
EXPOSE 8002 8082

# The actual command will be provided by docker-compose.yml
CMD ["python", "-m", "pifunc", "run", "calculator/service.py"]
