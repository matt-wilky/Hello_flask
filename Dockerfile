# Use the base image with Python pre-installed
FROM python:3.12

# Install the ODBC Driver 17 for SQL Server
RUN apt-get update && \
    apt-get install -y curl gnupg && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Install other dependencies
RUN apt-get install -y unixodbc-dev

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install Python dependencies
RUN pip install -r requirements3.txt

# Expose the port on which your Flask app runs
EXPOSE 443

# Run the Flask application
CMD ["python", "app.py"]