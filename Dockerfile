FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Cloud Run requires listening on $PORT environment variable
ENV PORT=8080

# Use gunicorn for production (better than waitress for Cloud Run)
RUN pip install gunicorn

# Run the application
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 'app:create_app()'
