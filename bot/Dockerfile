# Use the official Python image as the base image
FROM python:3.10

# Set the working directory inside the container
WORKDIR /api

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# REQUIRED: Change these if you plan on hosting this
# outside of localhost
ENV LAVALINK_URI=http://lavalink:5090
ENV REDIRECT_URI=http://0.0.0.0:5090/auth/redirect
ENV REDIRECT_LOC=http://0.0.0.0:3000/posts/server-select

# REQUIRED: Env variables for your bot token, client_id, and client_secret
# These can be found in the developer portal under Bot and OAuth2 -> General 
ENV BOT_TOKEN=
ENV BOT_CLIENT_ID=
ENV BOT_CLIENT_SECRET=

# OPTIONAL: Leave these as blank
ENV SPOTIFY_CLIENT_ID=
ENV SPOTIFY_CLIENT_SECRET=


# Copy the entire content of the current directory to the container
COPY . .

# Expose the port on which your FastAPI app will run 
EXPOSE 5090

# Run the FastAPI app with uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5090"]
