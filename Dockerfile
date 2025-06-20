# Use a lightweight official Python image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the Flask app and client code into the container
COPY blender_mcp_api.py .
COPY client_mcp.py .

# Install Python dependencies
RUN pip install Flask

# Install curl for debugging purposes (optional for production)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Expose the port the Flask app runs on
EXPOSE 5005

# Command to run the Flask app
CMD ["python", "blender_mcp_api.py"]