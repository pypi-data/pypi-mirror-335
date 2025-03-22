FROM python:3.11-slim

WORKDIR /app

# Copy the entire project directory
COPY . .

# Install dependencies directly without using a virtual environment
# This is common practice in Docker as the container itself provides isolation
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Install the local package (uncomment if needed)
# RUN pip install -e .

# Expose ports for HTTP and WebSocket
EXPOSE 8002 8082

# The actual command will be provided by docker-compose.yml
#CMD ["python", "-m", "pifunc", "run", "service.py"]
#python -m pifunc run service.py
CMD ["python", "service.py"]
#python service.py