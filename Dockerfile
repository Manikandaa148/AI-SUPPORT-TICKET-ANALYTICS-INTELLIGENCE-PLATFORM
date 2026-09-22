FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose ports for FastAPI and Streamlit
EXPOSE 8000 8501

# Run a simple script that launches both via subprocess, or just default to backend
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
