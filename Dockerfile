# Use python version 3.10
FROM python:3.10-bookworm

# Change workdir inside container
WORKDIR /flask-app

# Copy the application into the container
COPY . /flask-app

# Install dependencies
RUN pip install --no-cache-dir -r /flask-app/requirements.txt

# Expose port
EXPOSE 5000

ENV PYTHONUNBUFFERED=1

# Command to run the application, first initializing DB
# This is overruled by the command in docker-compose.yml
#CMD ["python", "-m", "app.initialize_db"]
#CMD ["python", "-m", "app.initialize_db", "&&", "gunicorn", "--workers", "4", "-b", "0.0.0.0:5000", "--preload", "--pythonpath", "flask-app", "--log-level=debug", "app.wsgi:app"]
