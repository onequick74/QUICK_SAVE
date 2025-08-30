# Use maintained Python base image
FROM python:3.10-slim-bullseye

# Install dependencies
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    git curl wget python3-pip bash neofetch ffmpeg software-properties-common && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir wheel && \
    pip install --no-cache-dir -r requirements.txt

# Set workdir
WORKDIR /app

# Copy source code
COPY . .

# Expose port
EXPOSE 5000

# Start application
CMD flask run -h 0.0.0.0 -p 5000 & python3 -m jaat
