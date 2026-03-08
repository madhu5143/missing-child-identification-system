# --- Stage 1: Build Frontend ---
FROM node:20-slim AS frontend-builder
WORKDIR /app
COPY frontend/package*.json ./frontend/
WORKDIR /app/frontend
RUN npm install
COPY frontend/ ./
RUN npm run build

# --- Stage 2: Backend & Runtime ---
FROM python:3.10-slim

# Install system dependencies for OpenCV and Face Recognition
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy built frontend from Stage 1 to backend/static
COPY --from=frontend-builder /app/frontend/dist ./backend/static

# Copy startup script
COPY start.sh ./
RUN chmod +x start.sh

# Environment variables
ENV PORT=8000
EXPOSE 8000

CMD ["bash", "start.sh"]