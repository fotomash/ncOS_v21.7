# Stage 1: Build the application with Poetry
FROM python:3.10-slim as builder

# Set working directory
WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy only the dependency files to leverage Docker layer caching
COPY poetry.lock pyproject.toml ./

# Install dependencies, without creating a virtualenv
RUN poetry config virtualenvs.create false && poetry install --no-dev --no-root

# Stage 2: Create the final production image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy the installed dependencies from the builder stage
COPY --from=builder /app /app

# Copy the application source code
COPY ./src /app/src
COPY ./main.py ./cli.py ./

# Copy configuration files
COPY ./config /app/config

# Set environment variables
ENV PYTHONPATH=/app
ENV NCOS_ENV=production

# Expose ports for the API and Dashboard
EXPOSE 8000
EXPOSE 8080

# Command to run the application
CMD ["python", "main.py"]
