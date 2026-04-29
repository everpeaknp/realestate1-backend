# Use official Python 3.11 slim image (3.11 often has better wheel support for ML)
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT 8000

# Set working directory
WORKDIR /app

# Install system dependencies
# We keep build-essential and gcc just in case, but aim to avoid using them
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install heavy ML libraries first using only-binary to avoid compilation
RUN pip install --no-cache-dir --only-binary :all: numpy spacy thinc blis sentence-transformers

# Install the rest of the requirements
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Pre-download SentenceTransformer model to bake it into the image
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy the rest of the application code
COPY . /app/

# Create a non-root user for security and set permissions
RUN adduser --disabled-password --gecos "" django-user && \
    chmod +x /app/start.sh && \
    chown -R django-user:django-user /app

USER django-user

# Expose the port
EXPOSE 8000

# Run the start script
CMD ["/app/start.sh"]
