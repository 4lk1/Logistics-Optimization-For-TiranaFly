FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for PostGIS and Geospatial libraries
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    binutils \
    libproj-dev \
    gdal-bin \
    python3-gdal \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
