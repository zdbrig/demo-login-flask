#!/bin/bash

# Define the path to the instance directory and database file
INSTANCE_DIR="./instance"
DB_PATH="$INSTANCE_DIR/app.db"

# Check if the instance directory exists, if not, create it
if [ ! -d "$INSTANCE_DIR" ]; then
  echo "Creating instance directory..."
  mkdir -p "$INSTANCE_DIR"
fi

# Check if the database file exists
if [ ! -f "$DB_PATH" ]; then
  echo "Creating SQLite database file at $DB_PATH..."
  touch "$DB_PATH"
else
  echo "Database file already exists at $DB_PATH."
fi

# Build and run the Docker containers
docker-compose up --build
