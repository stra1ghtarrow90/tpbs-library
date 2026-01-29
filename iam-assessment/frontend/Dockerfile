FROM node:20

WORKDIR /app/frontend

COPY frontend/package.json /app/frontend/package.json
COPY frontend/vite.config.js /app/frontend/vite.config.js
RUN npm install

COPY frontend/index.html /app/frontend/index.html
COPY frontend/src /app/frontend/src

CMD ["npm", "run", "dev"]
