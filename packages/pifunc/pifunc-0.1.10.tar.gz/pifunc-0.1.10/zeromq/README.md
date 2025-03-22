the ZeroMQAdapter code
the `.env` file to include ZeroMQ configuration:


To use this setup:

1. Install the required packages:
   ```bash
   pip install python-dotenv pyzmq psutil
   ```

2. Start the ZeroMQ service:
   ```bash
   python zeromq-service.py
   ```

3. In another terminal, run the test client:
   ```bash
   chmod +x zeromq-client.sh
   ./zeromq-client.sh
   ```

This implementation is more robust and follows best practices for environment configuration and error handling.