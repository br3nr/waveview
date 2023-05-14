# Use the official Node.js image as the base
FROM node:18-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy the package.json and package-lock.json files
COPY package*.json ./

# Install the project dependencies
RUN npm ci

# Copy the rest of the application code
COPY . .

ENV NEXT_PUBLIC_WEBSOCKET_URL=ws://192.168.0.153:5090/ws

# Build the Next.js application
RUN npm run build

# Expose the default Next.js port (3000)
EXPOSE 3000

# Start the Next.js application
CMD ["npm", "start"]
