# Use a base image with Python and cron installed
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the requirements.txt file to the container and install the packages
COPY requirements.txt /tmp/
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r /tmp/requirements.txt

COPY . /app/

# CMD ["python", "get-sonarqube-data.py", "--date", "16-05-2024"]
CMD ["python", "data-analyze.py"]