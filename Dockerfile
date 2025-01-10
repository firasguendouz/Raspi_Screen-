# Base image for Raspberry Pi with Python
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    hostapd dnsmasq iw net-tools \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install -r requirements.txt

# Expose the Flask web server port
EXPOSE 80

# Command to run the application
CMD ["python3", "main.py"]
