FROM python:3.10-slim

WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and migration settings
COPY backend/ ./backend/
COPY alembic/ ./alembic/
COPY alembic.ini .
COPY .env* ./

EXPOSE 7860

# Add backend directory to path so imports work correctly
ENV PYTHONPATH=/app/backend

# Run migrations and start FastAPI server
CMD ["sh", "-c", "alembic upgrade head && uvicorn backend.server:app --host 0.0.0.0 --port ${PORT:-7860}"]
