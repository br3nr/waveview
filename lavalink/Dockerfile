# Start from a base image with Java installed
FROM openjdk:11

# Set the working directory inside the container
WORKDIR /lavalink

# Copy the Lavalink JAR file to the container
COPY Lavalink.jar .

# Copy the application.yml file to the container
COPY application.yml .

ENV PLUGINS_SPOTIFY_CLIENTID=
ENV PLUGINS_SPOTIFY_CLIENTSECRET=

# Expose the default port used by Lavalink
EXPOSE 2333

# Set the command to run when the container starts
CMD ["java", "-jar", "Lavalink.jar"]
