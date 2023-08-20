# FROM python:3.8-slim

# # Set the working directory in docker
# WORKDIR /app

# # Copy the dependencies file to the working directory
# COPY requirements.txt .

# # Install any dependencies
# RUN pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt

# # Copy the content of the local src directory to the working directory
# COPY generateAudio.py .

# ENV NAME DockerPython

# # Expose the application on port 5000
# EXPOSE 5000

# # Specify the command to run on container start
# CMD ["python", "generateAudio.py"]

# Use an official Python runtime as a base image
# FROM python:3.8-slim
# FROM python:3.8
# Use PyTorch base image
# Use PyTorch base image
# FROM pytorch/pytorch:1.9.0-cuda11.1-cudnn8-runtime
FROM pytorch/pytorch

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install required system dependencies
RUN apt-get clean && \
    apt-get update -y && \
    apt-get dist-upgrade -y && \
    apt-get install -y libsndfile1 libgomp1 sox && \
    rm -rf /var/lib/apt/lists/*

# Install required Python dependencies
RUN pip install --upgrade pip && \
    pip install boto3 transformers torchaudio librosa flask torch torchvision torchaudio

# Expose port 5000
EXPOSE 5000

# Run whisper.py when the container launches
CMD ["python", "whisper.py"]




# Use an official PyTorch base image as a parent image
# FROM pytorch/pytorch:1.9.0-cuda11.1-cudnn8-runtime


# # Set the working directory in the container
# WORKDIR /app

# # Copy the current directory contents into the container at /app
# COPY . /app

# # Install Python dependencies
# RUN pip install --no-cache-dir -r requirements.txt

# # Expose port 5000 for the Flask app to listen on
# EXPOSE 5000

# # Run app.py when the container launches
# CMD ["python", "whisper.py"]


# Use PyTorch as the base image for the building stage
# FROM pytorch/pytorch:1.9.0-cuda11.1-cudnn8-runtime as builder

# WORKDIR /app

# COPY requirements.txt .
# RUN pip install -r requirements.txt

# COPY . .

# # Use a lightweight Python image for the runtime stage
# FROM python:3.9-slim as runner

# WORKDIR /app

# # Copy installed libraries from builder
# COPY --from=builder /root/.local /root/.local

# # Ensure scripts in .local are usable:
# ENV PATH=/root/.local/bin:$PATH

# COPY . .

# CMD ["flask", "run"]
