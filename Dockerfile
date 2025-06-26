FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy only necessary files
COPY my_package/ my_package/
COPY pyproject.toml ./
COPY requirements.txt ./

# Install dependencies if any
RUN pip install --no-cache-dir .

# Default command
CMD ["python3"]
