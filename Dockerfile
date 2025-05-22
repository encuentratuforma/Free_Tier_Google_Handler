# 1. Imagen base con Python 3.10
FROM python:3.10-slim

# 2. Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# 3. Copiar dependencias y código fuente
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

# 4. Exponer el puerto que usa Gunicorn
EXPOSE 8080

# 5. Comando de inicio usando Gunicorn (4 workers)
CMD ["gunicorn", "-w", "4", "-b", ":8080", "main:app"]
