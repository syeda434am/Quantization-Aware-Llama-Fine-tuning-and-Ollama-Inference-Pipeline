# Use the latest official PyTorch image with CUDA and cuDNN support
FROM nvidia/cuda:12.0.1-cudnn8-runtime-ubuntu20.04

# Set the working directory inside the container
WORKDIR /llm-utility

ARG DEBIAN_FRONTEND=noninteractive

# Install system packages, including Docker and Google Cloud SDK, and clean up unnecessary files
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3-pip \
    python3-dev \
    git \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    && curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
    && apt-get update \
    && apt-get install -y docker-ce docker-ce-cli containerd.io google-cloud-sdk \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Ensure Python files are executable and no additional file permission issues exist
RUN find . -name "*.py" -exec chmod +x {} \;

RUN chmod +x entrypoint.sh

# Set the entrypoint to execute the entrypoint script
ENTRYPOINT ["/entrypoint.sh"]