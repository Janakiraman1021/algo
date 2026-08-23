FROM node:20-alpine

WORKDIR /app

COPY package*.json tsconfig.json ./
RUN npm install

COPY src ./src
RUN npm run build

EXPOSE 4020

CMD ["npm", "start"]
