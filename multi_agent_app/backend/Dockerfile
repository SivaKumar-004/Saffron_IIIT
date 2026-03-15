FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
# We expect the `app` folder to be copied to `/app/app`
COPY ./app /app/app

# Expose port (internal)
EXPOSE 8000

# Run uvicorn server
# Make sure to run the main module inside the app folder
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
