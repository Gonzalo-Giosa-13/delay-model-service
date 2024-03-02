# Usar una imagen base de Python 3.11
FROM python:3.11.5-slim

# Definir el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar el archivo de requerimientos primero para aprovechar la caché de capas de Docker
COPY ./challenge/requirements.txt .

# Instalar las dependencias del archivo requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de los archivos necesarios para la aplicación
COPY ./challenge/reg_model_2.joblib .
COPY ./challenge/api.py .

# Exponer el puerto 8000 para la aplicación FastAPI
EXPOSE 8080

# Definir el comando para ejecutar la aplicación usando uvicorn
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]


