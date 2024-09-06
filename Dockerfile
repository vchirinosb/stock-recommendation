                       # Use an official Python runtime as a parent image
FROM python:3.12.5-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install pip and necessary Python packages
RUN apt-get update && apt-get install -y curl && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    pip install --no-cache-dir -r requirements.txt

# Pull the specific model from Ollama
RUN ollama pull llama3.1:8b

# Expose the port for Uvicorn and Streamlit
EXPOSE 8000 8501

# Command to run both Uvicorn and Streamlit
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --reload & streamlit run streamlit_app.py"]
