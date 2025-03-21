# Use Python 3.8 base image
FROM python:3.12

# Install system dependencies (for spaCy and its dependencies)
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libatlas-base-dev \
    gfortran \
    curl \
    git \
    wget

# Upgrade pip, setuptools, and wheel (to ensure we're using the latest version)
RUN pip install --upgrade pip setuptools wheel

# Install spaCy (make sure the compatible version with Python 3.8 is installed)
RUN pip3 install spacy==3.7.5  # Change this to a specific compatible version, e.g. 2.2.4

# Download the necessary spaCy language model (en_core_web_sm)
RUN python -m spacy download en_core_web_sm

# Install required Python dependencies
RUN pip3 install tqdm
RUN pip3 install Cython
RUN pip install xaif_eval==0.0.9
RUN pip3 install markdown2
RUN pip3 install flask-cors



# Copy the application files into the container
COPY . /app

# Set the working directory to /app
WORKDIR /app

# Install additional Python dependencies from requirements.txt
RUN pip install -r requirements.txt

# Expose port 5008 for the Flask app
EXPOSE 5005

# Set the default command to run the application
CMD ["python", "./main.py"]
