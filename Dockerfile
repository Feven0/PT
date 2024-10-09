FROM python:3.12-slim

ENV STRAPI_STAGE=dev


RUn pip install --upgrade pip

WORKDIR /app

COPY ./api/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

###copy all files in currrent dir to WORKDIR/
COPY . .

ENV STRAPI_STAGE=dev

EXPOSE 4500
RUN export nworkers=$(nproc --all)
RUN echo "nworkers=$nworkers"
ENTRYPOINT uvicorn app:app --host 0.0.0.0 --port 4500 

