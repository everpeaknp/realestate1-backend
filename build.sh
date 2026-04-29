#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Updating pip and build tools..."
python -m pip install --upgrade pip setuptools wheel

echo "Installing heavy ML dependencies as binary wheels..."
# Force only-binary for these packages to avoid expensive and failure-prone compilation on Render
python -m pip install --only-binary :all: \
    "numpy>=1.19.0" \
    "blis>=0.7.8,<0.8.0" \
    "thinc>=8.2.2,<8.3.0" \
    "spacy==3.7.4" \
    "sentence-transformers==2.6.1"

echo "Installing remaining requirements from requirements.txt..."
# Use --prefer-binary to avoid source builds for other packages where possible
pip install --prefer-binary -r requirements.txt

echo "Installing spaCy English model..."
python -m spacy download en_core_web_sm

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Build script completed successfully!"
