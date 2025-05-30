FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends apt-utils
RUN apt-get -y install curl
RUN apt-get install libgomp1

ENV STRAPI_STAGE=dev-prod


RUn pip install --upgrade pip

WORKDIR /app

COPY ./api/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

###copy all files in currrent dir to WORKDIR/
COPY . .

ENV STRAPI_STAGE=dev-prod

EXPOSE 4900
RUN export nworkers=$(nproc --all)
RUN echo "nworkers=$nworkers"
ENTRYPOINT uvicorn app:app --host 0.0.0.0 --port 4900

