# Use the official Python image as the base image
FROM python:3.9-alpine

# Create a new user and group called "appuser"
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install the dependencies; --no-cache-dir flag is used to avoid storing the downloaded packages in the Docker image's cache
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files to the container
COPY . .

# Change the ownership of the application files to the "appuser" and "appgroup"
RUN chown -R appuser:appgroup .

# Change the permissions of the application files to be read-only for others
RUN chmod -R o+r .

# Switch to the "appuser"
USER appuser

# Expose port 5000 for the application
EXPOSE 5000

# Start the application when the container starts
CMD ["python", "app.py"]
