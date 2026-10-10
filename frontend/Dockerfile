FROM node:26-slim AS build

WORKDIR /app

COPY package.json .
RUN npm install

COPY . .

FROM node:26-slim

WORKDIR /app
RUN chown node:node /app

COPY --from=build --chown=node:node /app .

USER 1000:1000

EXPOSE 3001

CMD ["npm", "run", "dev"]
