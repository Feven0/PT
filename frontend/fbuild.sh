
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

elif [ $branch_name == "main" ] || [ $branch_name == "prod" ]; then
    echo "******Running Production Environment******"
    export yarntarget="start"
    export npmtarget="start"
    export NODE_ENV="production"

else
    echo "******Running Development Environment******"
    export yarntarget="develop"
    export npmtarget="develop"
    export NODE_ENV="development"

fi

name="parrot"

#========================================= 
#       write Dockerfile
#=========================================

cat <<'EOF' >> Dockerfile.local
# Stage 1: Build
FROM node:18-alpine AS build
# Set the working directory inside the container
WORKDIR /app
# Copy package.json and package-lock.json (or yarn.lock) into the container
COPY package.json ./
# Install the dependencies
RUN npm install
# Copy the entire project into the container
COPY . .
# Build the app for production
RUN npm run build
# Stage 2: Serve
FROM nginx:alpine
# Copy the build output from the previous stage to Nginx's HTML directory
COPY --from=build /app/dist /usr/share/nginx/html
# Expose port 80
EXPOSE 80
# Start Nginx server
CMD ["nginx", "-g", "daemon off;"]
EOF

cat <<EOF > Dockerfile
FROM node:18-alpine

ENV NODE_ENV=${NODE_ENV}
ENV NODE_OPTIONS=--max-old-space-size=8192 
WORKDIR /app
EOF


cat <<'EOF' >> Dockerfile
ENV PATH /app/node_modules/bin:$PATH
EOF

cat <<EOF >> Dockerfile
COPY ./package*.json /app/
COPY ./tsconfig.json /app/


RUN npm install 
RUN npm install -g serve

COPY . /app
RUN npm run build

EXPOSE 3500
CMD ["serve", "-s", "build"]

EOF

#=========================================
#       write .env
#=========================================
cat <<EOF > .env
NODE_ENV=${NODE_ENV}
VITE_REACT_APP_BACKEND_URL= https://dev-parrot.10academy.org
EOF

#=========================================
#       write docker-compose.yml
#=========================================
cat <<EOF > docker-compose.yml
version: '3.7'

services:
  $name:
    container_name: $name
    image: $name
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "3500:3500"
    env_file:
      - .env
    stdin_open: true
    tty: true

# version: '3'
# services:
#   $name:
#     build:
#       context: .
#       dockerfile: Dockerfile
#     ports:
#       - "3500:3500"
#     env_file:
#       - .env

EOF

echo "******Done!******"



echo "******Building Docker Image: $name******"
docker-compose down || echo "$name instance is not running"
docker rm $(docker ps -a -q)

#bash env_setup.sh
docker-compose build 
docker-compose up --force-recreate -d 
docker ps
