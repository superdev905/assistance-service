FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

COPY ./requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

COPY ./app /app
COPY ./.env /.env
COPY ./alembic.ini /alembic.ini
COPY ./config.cfg /config.cfg

EXPOSE 80:80