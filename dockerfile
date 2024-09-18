FROM python:3.9

# Set the working directory in the container
WORKDIR /app

ADD ./requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

ADD . /app
# Install system dependencies
RUN apt-get update && apt-get install -y \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx



# Copy the current directory contents into the container at /app
COPY . /app



# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV NAME World

# Run the command to start uWSGI
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
