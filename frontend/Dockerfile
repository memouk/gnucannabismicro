FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html /usr/share/nginx/html/index.html
COPY main.jsx /usr/share/nginx/html/main.jsx
COPY styles.css /usr/share/nginx/html/styles.css

EXPOSE 80
