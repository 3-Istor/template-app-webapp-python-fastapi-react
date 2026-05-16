# Étape de construction
FROM node:20-slim AS build

WORKDIR /app

COPY package.json .
RUN npm install

COPY . .


FROM node:20-slim

WORKDIR /app

COPY --from=build /app .

EXPOSE 3001

CMD ["npm", "run", "dev"]
