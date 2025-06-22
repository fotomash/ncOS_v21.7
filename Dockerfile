FROM python:3.10-slim

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-root

COPY . .

ENV PYTHONUNBUFFERED=1

EXPOSE 8008

CMD ["python", "ncos_unified_core.py"]
