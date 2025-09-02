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

# Expose port
EXPOSE 5000

# Run the app
CMD ["bash", "-c", "flask run -h 0.0.0.0 -p 5000 & python3 -m devgagan"]
