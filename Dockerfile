# Use python version 3.10
FROM python:3.10-bookworm

# Change workdir inside container
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application into the container
COPY . /app

# Expose port
EXPOSE 5000

# Run application
CMD ["python", "startup.py"]
