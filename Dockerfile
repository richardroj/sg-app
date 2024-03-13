# Usa una imagen base de Python
FROM python:3.9

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el contenido del directorio actual al directorio de trabajo en el contenedor
COPY . /app

# Instala las dependencias necesarias
RUN pip install -r requirements.txt

# Expone el puerto 5000 para que Flask pueda escuchar las solicitudes
EXPOSE 5000

# Define el comando para ejecutar la aplicación Flask

CMD ["python", "app.py"]

