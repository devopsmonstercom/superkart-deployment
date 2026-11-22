# Using a lightweight Python base image
FROM python:3.12-slim

# Setting the working directory inside the container
WORKDIR /app

# Copying and installing the dependencies first (to take advantage of Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copying the application code and the serialized model
COPY app.py superkart_model.joblib ./

# Exposing the port the API runs on
EXPOSE 7860

# Starting the Flask app with gunicorn (2 workers) on port 7860
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:7860", "app:superkart_api"]
