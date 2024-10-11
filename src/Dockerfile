
FROM python:3.11-slim AS builder

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY requirements_test.txt requirements_test.txt
ARG ENV
RUN if [ "$ENV" = "test" ]; then \
    pip install --no-cache-dir -r requirements_test.txt; \
    fi;

FROM python:3.11-slim AS app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY --from=builder /usr/local /usr/local

ENV PATH=/usr/local/bin:$PATH

COPY shopAPI/ /shopAPI/shopAPI/
COPY alembic/ /shopAPI/alembic/
COPY scripts/ /shopAPI/scripts/
COPY alembic.ini main.py /shopAPI/

WORKDIR /shopAPI

FROM app AS test

COPY tests/ /shopAPI/tests/
COPY pytest.ini /shopAPI/
