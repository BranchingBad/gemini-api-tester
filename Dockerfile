# Dockerfile

ARG GEMINI_API_KEY=

# Stage 1: Build the Python application
FROM python:3.9-slim AS build

WORKDIR /app

# COPY requirements first to leverage Docker's layer caching
COPY requirements.txt .
# Install dependencies (will now include Pillow)
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files (app.py and gemini-test.py)
COPY app.py .
COPY gemini-test.py . 

# Stage 2: Serve the front end and run the backend
FROM python:3.9-slim

WORKDIR /app

ENV GEMINI_API_KEY=${GEMINI_API_KEY}

# Copy dependencies from the build stage
# Copy the *installed* dependencies, not the whole site-packages
COPY --from=build /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=build /app/app.py /app/

# Copy the HTML file into the correct directory.
COPY gemini_frontend.html /app/static_html/gemini_frontend.html

EXPOSE 5000

CMD ["python", "app.py"]