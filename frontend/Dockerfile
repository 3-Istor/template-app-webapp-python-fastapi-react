FROM node:26-slim AS build

WORKDIR /app

COPY package.json .
RUN npm install

COPY . .
RUN npm run build

FROM nginxinc/nginx-unprivileged:1.31.7-alpine

# The tag lags behind Alpine security fixes; take them at build time.
USER root
RUN apk upgrade --no-cache

# The image renders /etc/nginx/templates/*.template with envsubst at start,
# substituting only variables that are set, so nginx's own $uri survives.
ENV BACKEND_HOST=http://backend:8000
# Makes the image fill NGINX_LOCAL_RESOLVERS from /etc/resolv.conf.
ENV NGINX_ENTRYPOINT_LOCAL_RESOLVERS=1

COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html

# Back to the base image's non-root user after apk upgrade.
USER 101

EXPOSE 3001
