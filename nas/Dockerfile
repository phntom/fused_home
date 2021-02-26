FROM nginx:alpine

COPY *.conf /etc/nginx/conf.d/
COPY dhparam.pem tlv.home.kix.co.il/tlv.home.kix.co.il.key tlv.home.kix.co.il/fullchain.cer /etc/nginx/ssl/

RUN mkdir -pv /var/www/letsencrypt/nas && \
  mkdir -pv /var/www/letsencrypt/hass && \
  mkdir -pv /var/www/letsencrypt/grafana && \
  nginx -t && \
  touch /usr/share/nginx/html/google397854415bd64264.html
