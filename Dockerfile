                       # Use an official Python runtime as a parent image
FROM python:3.12.5-alpine

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port for Uvicorn and Streamlit
EXPOSE 8000 8501

# Command to run both Uvicorn and Streamlit
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --reload & streamlit run streamlit_app.py"]
