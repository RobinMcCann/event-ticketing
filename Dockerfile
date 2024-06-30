# Use python version 3.10
FROM python:3.10-slim

# Expose port
EXPOSE 5000

ENV PYTHONUNBUFFERED=1

# Change workdir inside container
WORKDIR /flask-app

COPY requirements.txt /flask-app/requirements.txt

# Install dependencies, do before copying the rest of the files to build quicker from cache
RUN pip install --no-cache-dir -r /flask-app/requirements.txt

# Copy the application into the container
COPY . /flask-app

# Create group and user
RUN groupadd -r app-user-group && useradd -g app-user-group app-user
# Set ownership and privileges to minimal
RUN chown -R app-user:app-user-group /flask-app
# Switch to user
USER app-user

# Command to run the application, first initializing DB
# This is overruled by the command in docker-compose.yml
CMD ["python", "-m", "app.initialize_db", "&&", "gunicorn", "--workers", "4", "-b", "0.0.0.0:5000", "--preload", "--pythonpath", "flask-app", "--log-level=debug", "app.wsgi:app"]
