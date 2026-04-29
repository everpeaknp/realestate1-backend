FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
# Tell pip NEVER to build from source for any package.
# This is the global equivalent of --only-binary :all:
ENV PIP_ONLY_BINARY=":all:"

WORKDIR /app

# Install system dependencies
# libpq-dev for psycopg2-binary
# libjpeg-dev, zlib1g-dev, etc. for Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip, setuptools, and wheel first
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# --- Step 1: Install blis as a pre-built binary wheel ---
# blis is a BUILD DEPENDENCY of thinc. By installing it here first as a binary,
# we prevent pip from compiling it from source in thinc's isolated build environment.
# We must use --no-build-isolation when installing thinc/spacy afterwards so that
# pip reuses these already-installed binary packages instead of recompiling.
RUN pip install --no-cache-dir --only-binary :all: \
    "blis>=0.7.8,<0.8.0" \
    "murmurhash>=1.0.2,<1.1.0" \
    "cymem>=2.0.2,<2.1.0" \
    "preshed>=3.0.2,<3.1.0"

# --- Step 2: Install numpy as binary (required by thinc/spacy) ---
RUN pip install --no-cache-dir --only-binary :all: "numpy>=1.19.0,<2.0.0"

# --- Step 3: Install thinc WITHOUT build isolation ---
# This forces pip to use the blis binary we already installed above
# instead of trying to compile blis inside an isolated build environment.
RUN pip install --no-cache-dir --no-build-isolation --only-binary :all: \
    "thinc>=8.2.2,<8.3.0"

# --- Step 4: Install spacy and sentence-transformers as binaries ---
RUN pip install --no-cache-dir --no-build-isolation --only-binary :all: \
    "spacy==3.7.4" \
    "sentence-transformers==2.6.1"

# --- Step 5: Copy requirements and install the rest ---
COPY requirements.txt /app/
# Install remaining requirements. spacy/thinc/blis are already installed above.
# psycopg2-binary has a wheel so this should be fine.
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

# Download spaCy model (small English model for NER)
RUN python -m spacy download en_core_web_sm

# Pre-download SentenceTransformer model to bake it into the image (avoids runtime latency)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy the rest of the application code
COPY . /app/

# Create a non-root user for security and set permissions
RUN adduser --disabled-password --gecos "" django-user && \
    chmod +x /app/start.sh && \
    chown -R django-user:django-user /app

USER django-user

EXPOSE 8000

CMD ["/app/start.sh"]
