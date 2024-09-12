# Flask Authentication Project

This is a Flask-based authentication project that uses Docker for containerization and SQLite as the database.

## Getting Started

Follow these instructions to set up and run the project.

### Prerequisites

- Docker installed on your machine
- Docker Compose installed on your machine

### Step 1: Set Up Environment Variables

First, you need to create an environment file from the provided sample and fill in the necessary values.

```bash
cp .env.sample .env
```

Open the .env file and update the values as needed. Here is an example of what the .env file might look like:

```ini
# .env
DATABASE_URL=sqlite:///instance/app.db
EMAIL_FROM=your_email@example.com
EMAIL_PASSWORD=your_email_password

```

### Step 2: Build and Run the Project

Use Docker Compose to build and run the project. This command will build the Docker images and start the containers as defined in the docker-compose.yml file.

```bash
docker-compose up --build
```

## Accessing the Application

Once the containers are up and running, you can access the application in your web browser at:

```
http://localhost:4000
```

## Stopping the Application

To stop the application and remove the containers, run:

```bash
docker-compose down
```

## Notes

- The SQLite database is stored locally in the instance directory.
- Any changes made to the database inside the Docker container will be reflected in the local app.db file.

## Troubleshooting

If you encounter any issues during setup or running the project, ensure that:

- Docker and Docker Compose are correctly installed.
- The .env file is properly configured with valid values.
- The necessary ports (e.g., 4000) are not blocked by your firewall or another application.