FROM python:3.11-slim

# Instalar dependencias necesarias para compilar mysqlclient
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    libssl-dev \
    && apt-get clean

# Crear directorio de trabajo
WORKDIR /app

# Copiar todo el proyecto al contenedor
COPY . /app/

# Instalar dependencias Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Comando de inicio para producción con gunicorn
CMD ["gunicorn", "sap.wsgi:application", "--bind", "0.0.0.0:8000"]
