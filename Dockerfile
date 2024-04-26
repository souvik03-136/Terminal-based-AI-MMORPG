# Use an official Python runtime as a parent image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Copy only the necessary files (excluding .env)
COPY ./*.py ./
COPY requirements.txt ./

# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV PORT=3000

# Command to run your application, allowing overriding the port with environment variable
CMD ["python", "server.py"]
