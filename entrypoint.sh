#!/bin/bash

# Initialize the database if it doesn't exist
if [ ! -d "migrations/versions" ]; then
    echo "Initializing database migrations..."
    flask db init
    flask db migrate -m "Initial migration."
    flask db upgrade
else
    echo "Migrations already initialized. Running upgrade..."
    flask db upgrade
fi


# Run the Flask application
flask run --host=0.0.0.0 --port=4000
