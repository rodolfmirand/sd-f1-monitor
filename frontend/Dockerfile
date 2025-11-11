FROM nginx:alpine
COPY . /usr/share/nginx/html
EXPOSE 80
CMD sh -c 'IP=$(hostname -i); echo "🏁 Frontend disponível em: http://localhost:8080 (ou http://$IP:80 dentro da rede Docker)"; nginx -g "daemon off;"'
