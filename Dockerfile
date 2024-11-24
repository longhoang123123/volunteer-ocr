FROM python:3.10-bookworm

ENV APPLICATION_SERVICE=/services

# set work directory
RUN mkdir -p $APPLICATION_SERVICE

# where the code lives
WORKDIR $APPLICATION_SERVICE

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
COPY pyproject.toml ./

RUN apt-get update && apt-get install -y \
    libzbar0 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools wheel && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry lock && \
    poetry install --no-dev && \
    pip install gunicorn


# copy project
COPY . $APPLICATION_SERVICE

CMD gunicorn app.main:main_app -w 1 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 --timeout 300
