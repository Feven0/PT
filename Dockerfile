FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

ENV STRAPI_STAGE=dev

RUn pip install --upgrade pip

WORKDIR /app

COPY ./api/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt


###copy all files in currrent dir to WORKDIR/
COPY . .

# CMD will be provided by the base image. Set ENV variables with -e

