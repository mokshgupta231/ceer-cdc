FROM python:3.9-slim as builder

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt /tmp

# Upgrade pip and Install dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Set command to run
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
