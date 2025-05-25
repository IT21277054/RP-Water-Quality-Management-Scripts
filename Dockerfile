# Use official Python image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory inside the container
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy Excel and Python script into /app
COPY Sample.xlsx ./Sample.xlsx
COPY ModbusScript.py ./ModbusScript.py

# Expose the Modbus TCP port
EXPOSE 5020

# Run the script
CMD ["python", "ModbusScript.py"]
