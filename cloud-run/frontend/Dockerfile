# Use the official Python image.
# https://hub.docker.com/_/python
FROM python:3.9-slim

# Allow statements and log messages to immediately appear in the Cloud Run logs.
ENV PYTHONUNBUFFERED True
ENV PORT 8080

# Copy application dependency manifests to the container image.
# Copying this separately prevents re-running pip install on every code change.
COPY /app/main.py /app/main.py
COPY /app/requirements.txt /app/requirements.txt

WORKDIR /app

# Install requirements
RUN pip install -r requirements.txt

# Expose ports.
EXPOSE $PORT

# Run the web service on container startup.
CMD streamlit run --server.port $PORT --server.enableCORS false main.py