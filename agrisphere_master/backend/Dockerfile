FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend app contents into /app/backend
COPY ./ /app/backend/

EXPOSE 8000

# Explicitly start FastAPI from the main file module in the backend dir
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
