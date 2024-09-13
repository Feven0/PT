#sudo chmod 777 -R ../tenx_auto_grade

target=${1:-"api"}
buildtype=${2:-"local"}
echo "Target = $target"
echo "Buildtype = $buildtype"

#-----------------------------------------------
#---- Setup necessary ENV variables ------------
#-----------------------------------------------
branch_name=$(git symbolic-ref -q HEAD)
branch_name=${branch_name##refs/heads/}
export branch_name=${branch_name:-HEAD}

if [ $branch_name == "prod" ]; then
    branch_name="prod"
    echo "******Running Production Frog Backend Environment******"
    export STRAPI_STAGE="apply"   
else
    branch_name="dev"
    echo "******Running Development Environment******"
    export STRAPI_STAGE="devapply"  
fi

source api/env_setup.sh
echo "build.sh: using envfile=$envfile.."

#build_arg=$(grep "GITHUB" $envfile | sed 's@^@--build-arg @g' | tr -d \" | paste -s -d " ")
#build_arg="${build_arg} --build-arg CACHEBUST=$(date +%s)"
#echo "build_arg=$build_arg"
function make_general_dockerfile(){
    build_arg=""

cat <<EOF > Dockerfile
FROM python:3.12-slim

ENV STRAPI_STAGE=${STRAPI_STAGE:-"dev"}


RUn pip install --upgrade pip

WORKDIR /app

COPY ${2:-./api}/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

###copy all files in currrent dir to WORKDIR/
COPY . .

ENV STRAPI_STAGE=${STRAPI_STAGE:-"dev"}

EXPOSE ${1:-5500}
RUN export nworkers=\$(nproc --all)
RUN echo "nworkers=\$nworkers"
ENTRYPOINT uvicorn ${3:-"app:app"} --host 0.0.0.0 --port ${1:-5500} 

EOF
}

function make_gunicorn_dockerfile(){
    #REF: https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker
    build_arg="-e APP_MODULE=app:app -e WEB_CONCURRENCY="4" -e TIMEOUT="120" -e KEEP_ALIVE="60" -e LOG_LEVEL="info" -e PORT=${1:-5500}"
    
cat <<EOF > Dockerfile
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

ENV STRAPI_STAGE=${STRAPI_STAGE:-"dev"}

RUn pip install --upgrade pip

WORKDIR /app

COPY ${2:-./api}/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt


###copy all files in currrent dir to WORKDIR/
COPY . .

# CMD will be provided by the base image. Set ENV variables with -e

EOF
}

#docker run --name my-redis -p 6379:6379 -d redis
#========================================= 
#       write Dockerfile
#=========================================

if [[ $branch_name == "prod" ]] || [[ $branch_name == "worker" ]]; then
    pyreq="./api"
    echo "PROD: Using Uvicorn ... "
    name="${branch_name}ipersona"
    port=4500
    tport=4500
    make_general_dockerfile $port $pyreq
    #make_gunicorn_dockerfile $port $pyreq
elif [[ $branch_name == "dev" ]]; then
    pyreq="./api"
    echo "DEV: Using Gunicorn multi workers... "
    name="ipersona"
    port=4500
    tport=4500
    #make_general_dockerfile $port $pyreq
    make_gunicorn_dockerfile $port $pyreq    
else
    echo "Using Dockerfile for General ... "
    name="${branch_name}ipersona"
    port=4500
    tport=4500
    pyreq="./api"
    make_general_dockerfile $port $pyreq
fi
echo "name=$name"
echo "port=$port"
echo "pyreq=$pyreq"

if [[ $branch_name == "prod" ]]; then
    echo "Backed Production Deployment: Exit after writing Dockerfile for ${branch_name} branch"
    exit
fi

#=========================================
#       write docker-compose.yml
#=========================================

cat <<EOF > docker-compose.yml
version: "3"
services:
  $name:
    container_name: $name
    build: .
    image: $name:latest
    restart: unless-stopped
    environment:
      - STRAPI_STAGE=$STRAPI_STAGE
      - PORT=$tport
      - APP_MODULE=app:app
      - WORKERS_PER_CORE=0.5
      - TIMEOUT=120
      - KEEP_ALIVE=60
      - LOG_LEVEL=info      - 
    networks:
      - ipersona_network    
    # volumes:
    #   - /mnt/efs:/mnt/efs
    expose:
      - $tport 
    ports:
      - "$port:$tport"

networks:
    ipersona_network:
        name: $name
        driver: bridge      

EOF

#    network_mode: "host"    

#-----------------------------------------------
#---- build image ------------
#-----------------------------------------------
docker-compose down --remove-orphans -t 0 $name

res=$(docker ps -aq)
if [[ ! -z $res ]]; then
    docker rm $res
fi

export PORT=$tport
docker-compose build $name
docker-compose up --remove-orphans --force-recreate -d $name
docker ps

echo "----- Logs so far ..-----"
echo "docker logs -f $(docker ps | head -2 | tail -1 | cut -d " " -f 1)"
docker logs -f $(docker ps | head -2 | tail -1 | cut -d " " -f 1)

#test
if [ $buildtype == "lambda" ]; then 
    echo "Pinging webserver endpoint: "
    payload="{"""resource""": """/""", """path""": """/""", """httpMethod""": """GET""", """requestContext""": {}, """multiValueQueryStringParameters""": null}"
    curl "http://localhost:${port}/2015-03-31/functions/function/invocations" -d $payload
fi  

echo ""
