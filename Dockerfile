# Use an official Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy dependency files first (for better caching)
COPY requirements.txt .

# Install system dependencies and Python packages
RUN apt-get update && apt-get install -y build-essential && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose Streamlit's default port
EXPOSE 8501

# Environment variables for Streamlit
ENV STREAMLIT_PORT=8501
ENV PYTHONUNBUFFERED=1

# Set Streamlit to listen on all interfaces (important for Docker)
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
