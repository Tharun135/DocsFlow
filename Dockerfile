FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 docsflow && \
    chown -R docsflow:docsflow /app
USER docsflow

# Expose port for development server
EXPOSE 8000

# Default command
CMD ["mkdocs", "serve", "--dev-addr=0.0.0.0:8000"]