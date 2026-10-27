FROM node:26-slim AS build

WORKDIR /app

COPY package.json .
RUN npm install

COPY . .
RUN npm run build

FROM nginxinc/nginx-unprivileged:1.31.7-alpine

# The image renders /etc/nginx/templates/*.template with envsubst at start,
# substituting only variables that are set, so nginx's own $uri survives.
ENV BACKEND_HOST=http://backend:8000
# Makes the image fill NGINX_LOCAL_RESOLVERS from /etc/resolv.conf.
ENV NGINX_ENTRYPOINT_LOCAL_RESOLVERS=1

COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html

# Restated from the base image so the Dockerfile scan sees a non-root user.
USER 101

EXPOSE 3001
