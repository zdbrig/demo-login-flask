#!/bin/bash

# Define the path to the database file
DB_PATH="./instance/app.db"

# Check if the database file exists
if [ ! -f "$DB_PATH" ]; then
  echo "Creating SQLite database file at $DB_PATH..."
  touch "$DB_PATH"
else
  echo "Database file already exists at $DB_PATH."
fi

# Build and run the Docker containers
docker-compose up --build
