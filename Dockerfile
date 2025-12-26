# Base image
FROM python:3.13-alpine As base

# Set work directory
WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir poetry==2.1.3 && \
    poetry config virtualenvs.create false

# Copy dependency files first
COPY pyproject.toml poetry.lock ./


# Set environment variables
ENV FLASK_APP=src:create_app
ENV FLASK_RUN_HOST=0.0.0.0
# Expose Flask port
EXPOSE 5000

# ---------- DEV ----------
FROM base AS dev

# Install dependencies (without creating a virtualenv)
RUN poetry install --no-interaction --no-ansi --no-root

# Copy app source
COPY . .

# Start the Flask app
CMD ["flask", "run"]

# ---------- PROD ----------
FROM base AS prod

RUN poetry install --no-interaction --no-ansi --no-root --only=main
# Copy app source
COPY . .


CMD ["gunicorn", "--bind", "0.0.0.0:5000", "src:create_app()"]
