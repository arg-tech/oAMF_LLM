# Use an official Python image as the base
FROM python:3.10

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Add Ollama to PATH (for safety)
ENV PATH="/root/.ollama/bin:$PATH"

# Download the DeepSeek-r1:7b model
RUN ollama pull deepseek-r1:7b

# Copy application files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the Flask port
EXPOSE 5030

# Start Ollama service and Flask app
CMD ollama serve & python app.py
