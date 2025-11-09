FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Configurar directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY pyproject.toml poetry.lock* ./

# Instalar Poetry
RUN pip install --no-cache-dir poetry

# Configurar Poetry para no crear virtualenv (ya estamos en contenedor)
RUN poetry config virtualenvs.create false

# Instalar dependencias del proyecto
RUN poetry install --no-interaction --no-ansi --no-root

# Descargar modelo de spaCy en español
RUN python -m spacy download es_core_news_md

# Copiar código fuente
COPY . .

# Exponer puertos
EXPOSE 8000 5555

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando por defecto (será sobrescrito por docker-compose)
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
