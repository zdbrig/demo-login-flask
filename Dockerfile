# Use the official Python image as a base image
FROM python:3.9-slim

# Install SQLite3 and any other needed packages
RUN apt-get update && apt-get install -y sqlite3

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install any needed Python packages specified in requirements.txt
RUN pip install -r requirements.txt

# Set environment variables
ENV FLASK_APP=run.py
ENV FLASK_ENV=development

# Copy the entrypoint script into the container
COPY entrypoint.sh /app/entrypoint.sh

# Make entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Expose port 4000 for the Flask app
EXPOSE 4000

# Run the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
