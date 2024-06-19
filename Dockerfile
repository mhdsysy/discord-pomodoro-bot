# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app
WORKDIR /app

# Copy .env file
COPY .env /app/.env

# Expose the port the app runs on
EXPOSE 8080

# Run the application
CMD ["python", "bot.py"]
