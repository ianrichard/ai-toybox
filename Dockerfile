FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Set Python path to include src directory
ENV PYTHONPATH=/app

# Enable reload by default for development
ENV RELOAD=True

# Expose the API port
EXPOSE 8000

# Set entry point to python script
ENTRYPOINT ["python", "src/server.py"]
