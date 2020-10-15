# FROM node:latest as intermediate

FROM nginx:latest

COPY nginx.conf /etc/nginx/conf.d/

# Copy build folder
COPY frontend_build /usr/share/nginx/html/