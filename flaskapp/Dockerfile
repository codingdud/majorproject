# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    cmake \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgtk2.0-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user
RUN useradd -m appuser

# Create a directory for certificates and copy ca.pem
RUN mkdir -p /etc/ssl/certs
COPY ca.pem /etc/ssl/certs/ca.pem

# Change ownership of the working directory and cert directory
RUN chown -R appuser:appuser /app /etc/ssl/certs

# Switch to the non-root user
USER appuser

# Make port 80 available to the world outside this container
EXPOSE 80

# Define FLASK_APP, FLASK_ENV, and POSTGRES_SSLROOTCERT
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV POSTGRES_SSLROOTCERT=/etc/ssl/certs/ca.pem

# Run gunicorn when the container launches
CMD ["gunicorn", "run:app", "-b", "0.0.0.0:80"]

