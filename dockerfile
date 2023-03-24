# Base image
FROM python:3.9-slim-buster

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port 5000 for Flask
EXPOSE 5000

# Start the Flask app
CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0"]
