# Usa una imagen de Python 3
FROM python:3.8-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de la aplicación
COPY . /app

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto
EXPOSE 8000

# Comando para iniciar la aplicación
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "main:app"]
