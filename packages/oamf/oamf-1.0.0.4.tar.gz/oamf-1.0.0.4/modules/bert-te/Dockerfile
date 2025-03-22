# Use an official Python runtime as a parent image
FROM python:3.9-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \  
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Create app directory
WORKDIR /app

# Install Python dependencies in a virtual environment
COPY requirements.txt .
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install -r requirements.txt

# Copy the application code to the image
COPY . .

# Use a non-root user for security
#RUN useradd --create-home appuser
#USER appuser

# Expose the port the app runs on
EXPOSE 5002

# Set the entry point for the container
ENTRYPOINT ["/opt/venv/bin/python"]
CMD ["./main.py"]
