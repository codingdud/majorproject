# Environment Setup and Docker Configuration

This document explains how the environment variables are set up and used in the project, as well as how to use the Dockerfile.

## Environment Variables

The project uses the following environment variables, which are stored in the `.env` file:

```
POSTGRES_DB=""
POSTGRES_USER=""
POSTGRES_PASSWORD=""
POSTGRES_HOST=""
POSTGRES_PORT=""
POSTGRES_SSLMODE=""
POSTGRES_SSLROOTCERT=""
SQLITE_DB_PATH=""
```

These variables are used to configure the PostgreSQL connection in the application.

## Configuration in `app/config.py`

The `app/config.py` file uses these environment variables to set up the database connection:

```python
POSTGRES_CONN_DETAILS = {
    'dbname': os.getenv('POSTGRES_DB'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': os.getenv('POSTGRES_HOST'),
    'port': os.getenv('POSTGRES_PORT'),
    'sslmode': os.getenv('POSTGRES_SSLMODE'),
    'sslrootcert': os.getenv('POSTGRES_SSLROOTCERT', 'ca.pem')
}

SQLALCHEMY_DATABASE_URI = (
    f"postgresql://{POSTGRES_CONN_DETAILS['user']}:{POSTGRES_CONN_DETAILS['password']}"
    f"@{POSTGRES_CONN_DETAILS['host']}:{POSTGRES_CONN_DETAILS['port']}"
    f"/{POSTGRES_CONN_DETAILS['dbname']}"
)
```

## Dockerfile Configuration

The Dockerfile is set up to use these environment variables:

1. It copies the `.env` file into the container:
   ```dockerfile
   COPY .env .env
   ```
2. It copies the SSL certificate (`ca.pem`) into the container:
   ```dockerfile
   COPY ca.pem /app/ca.pem
   ```
3. It sets the `POSTGRES_SSLROOTCERT` environment variable to the path of the SSL certificate in the container:
   ```dockerfile
   ENV POSTGRES_SSLROOTCERT=/app/ca.pem
   ```

This configuration allows the application to access the environment variables and the SSL certificate inside the Docker container.

## Relationship to postgres_conn_details

The environment variables in the `.env` file correspond directly to the `postgres_conn_details` dictionary mentioned in the problem statement:

```python
postgres_conn_details = {
    'dbname': '',              # POSTGRES_DB
    'user': '',                 # POSTGRES_USER
    'password': '', # POSTGRES_PASSWORD
    'host': '', # POSTGRES_HOST
    'port': '',                    # POSTGRES_PORT
    'sslmode': '',               # POSTGRES_SSLMODE
    'sslrootcert': '',            # POSTGRES_SSLROOTCERT
}
```

By using environment variables instead of hardcoding these values, we achieve better security and flexibility. The application can read these values from the environment, which are set when the Docker container is run.

## How to Use

To build and run the Docker container:

1. Ensure that the `.env` file and `ca.pem` are in the same directory as the Dockerfile.
2. Build the Docker image:
   ```
   docker build -t your-image-name .
   ```
3. Run the Docker container, using the environment variables from the `.env` file:
   ```
   docker run --env-file .env your-image-name
   ```

This setup ensures that the application in the Docker container will use the correct environment variables for connecting to the PostgreSQL database securely.


In this scenario, the environment variable will be taken from the Dockerfile definition, not from the .env file. Here's why: [1]

Dockerfile ENV instruction: [2] The line ENV POSTGRES_SSLROOTCERT=/etc/ssl/certs/ca.pem in your Dockerfile sets an environment variable that will be available inside the container when it runs.

Docker build process: When you build your Docker image, the ENV instruction in the Dockerfile is processed and baked into the image. This means the environment variable is set as part of the container's environment.

Container runtime: When you run a container from this image, the environment variable POSTGRES_SSLROOTCERT will already be set to /etc/ssl/certs/ca.pem.

Python's os.getenv(): When your Python code runs os.getenv('POSTGRES_SSLROOTCERT', 'ca.pem'), it will first look for the POSTGRES_SSLROOTCERT environment variable in the container's environment. Since it's already set by the Dockerfile, it will use that value ( /etc/ssl/certs/ca.pem).

.env file: The .env file is typically used for local development or when explicitly loaded by your application. In a Docker context, it's not automatically used unless you specifically configure your application or Docker setup to load it.

So, in this case, os.getenv('POSTGRES_SSLROOTCERT', 'ca.pem') will return /etc/ssl/certs/ca.pem, which is the value set in the Dockerfile.

If you want to override the value from the Dockerfile:

You can pass an environment variable when running the container:

docker run -e POSTGRES_SSLROOTCERT=new_value ...

Copy

Insert at cursor
text
If using docker-compose, you can set it in the docker-compose.yml file:

environment:<p></p>

Copy

Insert at cursor
yaml
You can also use the --env-file option with docker run to specify a .env file, but this is less common when you're already using a Dockerfile with ENV instructions.

Remember, environment variables set at runtime (like with docker run -e) will override those set in the Dockerfile.