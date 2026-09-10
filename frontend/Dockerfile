# Stage 1: Build React/Vite assets
FROM node:20-alpine AS build

WORKDIR /app

# Cache and install dependencies
COPY package*.json ./
RUN npm install

# Copy source code and build production distribution
COPY . .
RUN npm run build

# Stage 2: Serve production bundle with Nginx
FROM nginx:alpine

# Copy built assets from Stage 1 to Nginx default html directory
COPY --from=build /app/dist /usr/share/nginx/html

# Replace default Nginx configuration to support client-side SPA routing
RUN printf 'server {\n\
    listen 80;\n\
    server_name localhost;\n\
    location / {\n\
        root /usr/share/nginx/html;\n\
        index index.html index.htm;\n\
        try_files $uri $uri/ /index.html;\n\
    }\n\
}\n' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]