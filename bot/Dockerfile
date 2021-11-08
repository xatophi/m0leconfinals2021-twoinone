FROM node
RUN apt-get update && apt-get install -y chromium

WORKDIR /app
COPY package*.json ./

RUN npm install

COPY *.js ./

EXPOSE 9999

CMD ["node", "server.js"]
