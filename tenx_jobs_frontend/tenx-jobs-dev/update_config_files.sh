echo "******Checking ENV variables ...******"
if [ -z NODE_ENV ]; then echo "Env variables not set .."; exit; fi
if [ -z dnsprefix ]; then echo "Env variables not set .."; exit; fi
if [ -z npmtarget ]; then echo "Env variables not set .."; exit; fi

suffix=${dnsprefix:-'cms'}
echo "Writing .env.development Dockerfile and docker-compose.yml with SUFFIX=$suffix .."

#========================================= 
#       write .env
#=========================================
bn=${GITHUB_BASE_REF:-${GITHUB_REF#refs/heads/}}
if [[ "${branch_name:-$bn}" == "prod" ]]; then
echo "Generating .env for production ..."
cat <<EOF > .env
VITE_API_BACKEND_URL='https://cms.10academy.org'
VITE_API_LEAP_JOB_BACKEND_URL='https://frog.10academy.org'
VITE_API_BACKEND_STAGE = 'prod'
EOF
else
echo "Generating .env for development ..."
cat <<EOF > .env
VITE_API_BACKEND_URL='https://dev-cms.10academy.org'
VITE_API_LEAP_JOB_BACKEND_URL='https://dev-frog.10academy.org'
VITE_API_BACKEND_STAGE = 'dev'
EOF
fi



#========================================= 
#       write Dockerfile
#=========================================
cat <<EOF > Dockerfile
FROM node:18-alpine

ENV NODE_ENV=${NODE_ENV}


ENV NODE_OPTIONS=--max-old-space-size=8192 

WORKDIR /app
EOF


cat <<'EOF' >> Dockerfile
ENV PATH /app/node_modules/.bin:$PATH
EOF

cat <<EOF >> Dockerfile
COPY ./package.json /app/

COPY ./tsconfig.json /app/
# COPY ./package-lock.json /app/

RUN npm install 
RUN npm install -g serve

COPY . /app

RUN npm run build

EXPOSE 5173
CMD ["serve", "-s", "dist", "-p", "5173"]


EOF
