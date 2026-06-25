
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if needed (none are needed for pure python)
# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY dashboard.py .
COPY last_mile_delivery_cleaned.csv .

# Expose port 8080 (Cloud Run default)
EXPOSE 8080

# Configure Streamlit to run on port 8080 and bind to all addresses
ENTRYPOINT ["streamlit", "run", "dashboard.py", "--server.port=8080", "--server.address=0.0.0.0"]
