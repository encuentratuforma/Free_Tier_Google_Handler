# 1. Base image with Python 3.10
FROM python:3.10-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy dependencies and source code
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

# 4. Expose the port used by Gunicorn
EXPOSE 8080

# 5. Startup command using Gunicorn (4 workers)
CMD ["gunicorn", "-w", "4", "-b", ":8080", "main:app"]