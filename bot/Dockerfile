# Use the official Python image as the base image
FROM python:3.10

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variable in Docker
ENV SPOTIFY_CLIENT_ID=""
ENV SPOTIFY_CLIENT_SECRET=""
ENV DEV_CLIENT_ID=""

# Copy the entire content of the current directory to the container
COPY . .

# Expose the port on which your FastAPI app will run 
EXPOSE 5090

# Run the FastAPI app with uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5090"]
