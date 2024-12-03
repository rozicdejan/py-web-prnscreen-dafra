# Use a Python image with browser support
FROM python:3.11-slim-bullseye

RUN apt-get update && apt-get install -y \
    chromium-driver=120.0.6099.224-1~deb11u1 \
    chromium=120.0.6099.224-1~deb11u1 \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libx11-xcb1 \
    libxcb-dri3-0 \
    libxi6 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxtst6 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libatk1.0-0 \
    libcups2 \
    xdg-utils \
    fonts-liberation \
    && apt-get clean

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/usr/bin:${PATH}"

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Set the entrypoint command to run the script
CMD ["python", "main.py"]