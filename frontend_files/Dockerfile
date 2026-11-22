# Using a lightweight Python base image
FROM python:3.12-slim

# Setting the working directory inside the container
WORKDIR /app

# Copying and installing the dependencies first (to take advantage of Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copying the Streamlit app
COPY app.py .

# Exposing Streamlit's default port
EXPOSE 8501

# Starting the Streamlit app; CORS/XSRF are disabled so file uploads work through the Codespaces port-forwarding proxy
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", \
     "--server.enableCORS=false", "--server.enableXsrfProtection=false"]
