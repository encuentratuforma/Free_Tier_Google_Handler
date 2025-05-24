# 1. Use a lightweight official Python 3.10 base image
FROM python:3.10-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Install pip and Python dependencies early to leverage Docker caching
COPY src/requirements.txt requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of the application source code
COPY src/ .

# 5. Expose the port that Gunicorn will use
EXPOSE 8080

# 6. Run the Flask app using Gunicorn with 4 worker processes
CMD ["gunicorn", "-w", "4", "-b", ":8080", "main:app", "--timeout", "60", "--log-level", "info"]