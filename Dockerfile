FROM python:3.13-slim

WORKDIR /app

# Install system dependencies and Node.js (for npx subprocesses)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Set Python path to include src directory
ENV PYTHONPATH=/app/src

# Enable reload by default for development
ENV RELOAD=True

# Expose the API port
EXPOSE 8000

# Set entry point to python script (adjust as needed)
ENTRYPOINT ["python", "src/server.py"]