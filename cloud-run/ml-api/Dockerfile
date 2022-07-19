# Use the official Python image.
# https://hub.docker.com/_/python
FROM python:3.10-buster

# Allow statements and log messages to immediately appear in the Cloud Run logs.
ENV PYTHONUNBUFFERED True
ENV PORT 8080

# Copy application dependency manifests to the container image.
# Copying this separately prevents re-running pip install on every code change.
COPY /app/main.py /app/main.py
COPY /app/requirements.txt /app/requirements.txt
COPY /app/main.py /app/main.py
COPY /app/bart-large-cnn/ /app/bart-large-cnn/

WORKDIR /app

# Install requirements
RUN pip install -r requirements.txt

# Expose ports.
EXPOSE $PORT

# Run warmup to download Huggingface model to container.
# RUN python warmup.py

# Run the web service on container startup.
# Use gunicorn webserver with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
CMD exec gunicorn --bind 0.0.0.0:$PORT main:app --workers 1 --threads 8 --timeout 0