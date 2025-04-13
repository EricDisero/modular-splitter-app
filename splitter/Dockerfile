# Use NVIDIA CUDA base image with Python 3.9
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app:${PYTHONPATH}"
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3.9 \
    python3.9-dev \
    python3.9-venv \
    python3-pip \
    python3-setuptools \
    curl \
    ffmpeg \
    libsndfile1 \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python3.9 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application code
COPY . .

# Create directories for processing
RUN mkdir -p /tmp/splitter_temp/uploads \
    /tmp/splitter_temp/processed \
    /tmp/splitter_output

# Set appropriate permissions
RUN chmod -R 777 /tmp/splitter_temp /tmp/splitter_output

# Expose port
EXPOSE 9000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9000"]