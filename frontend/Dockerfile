FROM node:18-alpine

ENV NODE_ENV=development
ENV NODE_OPTIONS=--max-old-space-size=8192 
WORKDIR /app
ENV PATH /app/node_modules/bin:$PATH
COPY ./package.json /app/
COPY ./tsconfig.json /app/
COPY ./vite.config.ts /app/

RUN npm install 
RUN npm install -g serve

COPY . /app
RUN npm run build

EXPOSE 3500
CMD ["serve", "-s", "dist", "-l", "3500"]

