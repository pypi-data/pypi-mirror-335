FROM python:3.11-slim-buster

RUN DEBIAN_FRONTEND=noninteractive

COPY requirements.txt /app/

# Install the necessary packages
RUN apt-get update && \
    apt-get install -y python-dev && \
    pip install --upgrade pip && \
    pip install -r /app/requirements.txt && \
    rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
#COPY . /app

# Set the working directory in the container
WORKDIR /app

ENV PYTHONPATH "${PYTHONPATH}:src"

# Run the Python script
#ENTRYPOINT ["/usr/local/bin/python3", "src/main.py"]
CMD ["sh", "-c", "cd /app && bash"]

