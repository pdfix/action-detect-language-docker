# Use the official Debian slim image as a base
FROM debian:stable-slim

# Update system and Install python3
RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/lang-detect/


# Create a virtual environment and install dependencies
ENV VIRTUAL_ENV=venv
RUN python3 -m venv venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
COPY requirements.txt /usr/lang-detect/
RUN pip install --no-cache-dir -r requirements.txt


# Copy config and source codes
COPY config.json /usr/lang-detect/
COPY src/ /usr/lang-detect/src/


ENTRYPOINT ["/usr/lang-detect/venv/bin/python3", "/usr/lang-detect/src/main.py"]
