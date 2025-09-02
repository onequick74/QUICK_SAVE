FROM python:3.10-slim-bookworm

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ffmpeg \
    wget \
    bash \
    neofetch \
    software-properties-common \
    supervisor \
 && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python deps
RUN pip3 install --no-cache-dir -U pip wheel \
 && pip3 install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port for Flask
EXPOSE 5000

# Copy supervisor config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Run both processes with supervisord
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
