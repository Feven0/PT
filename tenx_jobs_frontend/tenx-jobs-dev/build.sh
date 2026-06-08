#sudo chmod 777 -R ../tenx-jobs

#-----------------------------------------------
#---- Setup necessary ENV variables ------------
#-----------------------------------------------
branch_name=$(git symbolic-ref -q HEAD)
branch_name=${branch_name##refs/heads/}
branch_name=${branch_name:-HEAD}

if [ $branch_name == "staging" ]; then
    echo "******Running Staging Environment******"
    export yarntarget="start"
    export npmtarget="start"
    export NODE_ENV="production"
    export dbname="strapistage"
    export dnsprefix='stage-cms'

elif [ $branch_name == "main" ] || [ $branch_name == "prod" ]; then
    echo "******Running Production Environment******"
    export yarntarget="start"
    export npmtarget="start"
    export NODE_ENV="production"
    export dbname="strapiprod"
    export dnsprefix='cms'

else
    echo "******Running Development Environment******"
    export yarntarget="develop"
    export npmtarget="develop"
    export NODE_ENV="development"
    export dbname="strapidev"
    export dnsprefix='dev-cms'

fi

name="leap"
port=5173
tport=5173
echo "name=$name"
echo "port=$port"

#========================================= 
#       write .env and Dockerfile
#=========================================
bash update_config_files.sh $1

#=========================================
#       write docker-compose.yml
#=========================================

cat <<EOF > docker-compose.yml
version: '3'
services:
  $name:
    container_name: $name
    build: .
    image: $name:latest
    restart: unless-stopped
    expose:
      - $tport 
    ports:
      - "$port:$tport"
    stdin_open: true
    tty: true

EOF

#-----------------------------------------------
#---- build image ------------
#-----------------------------------------------
docker-compose down -t 0 $name

res=$(docker ps -aq)
if [[ ! -z $res ]]; then
    docker rm $res
fi


docker-compose build ${build_arg} $name
docker-compose up --remove-orphans --force-recreate -d $name
docker ps

echo "----- Logs so far ..-----"
echo "docker logs -f $(docker ps | head -2 | tail -1 | cut -d " " -f 1)"
docker logs -f $(docker ps | head -2 | tail -1 | cut -d " " -f 1)



