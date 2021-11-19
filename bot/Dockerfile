FROM node
RUN apt-get update && apt-get install -y chromium

WORKDIR /app
COPY package*.json ./

RUN npm install

RUN groupadd appgroup && useradd -g appgroup appuser 

COPY *.js ./

EXPOSE 9999

USER appuser

CMD ["node", "server.js"]
