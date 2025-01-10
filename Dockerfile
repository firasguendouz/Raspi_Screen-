# Use a lightweight Raspberry Pi base image
FROM balenalib/raspberrypi3-debian:latest

# Environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Paris
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    libcairo2-dev \
    pkg-config \
    hostapd \
    dnsmasq \
    network-manager \
    curl \
    git \
    libgtk-3-dev \
    libwebkit2gtk-4.0-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/static /app/config && \
    chmod -R 600 /app/config || true

# Expose ports
EXPOSE 80 5001

# Default command to run the main application
CMD ["python3", "main.py"]

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:80 || exit 1
