FROM node:latest as build

# Clone repo
# Change into cloned repo
# Install packages and build project
RUN git clone https://github.com/RedstoneMedia/hatribute.de_Frontend.git && cd hatribute.de_Frontend/ && npm install && npm run build -- --prod

FROM nginx:latest

COPY nginx.conf /etc/nginx/conf.d/

#Copy build folder from build stage
COPY --from=build hatribute.de_Frontend/dist/Frontend /usr/share/nginx/html/