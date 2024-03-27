# Use an official Python runtime as a parent image
FROM python:3.10.12-slim-bullseye

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

#  create folder called /app/files
RUN mkdir /app/files

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that your application will run on
EXPOSE 8080

# Start the application using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
