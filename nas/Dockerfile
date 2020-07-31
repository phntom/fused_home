FROM nginx:1.18.0-alpine

COPY *.conf /etc/nginx/conf.d/
COPY dhparam.pem nas.tlv.home.kix.co.il.* /etc/nginx/ssl/
COPY google397854415bd64264.html /usr/share/nginx/html/

RUN mkdir -pv /var/www/letsencrypt/nas && \
  mkdir -pv /var/www/letsencrypt/hass && \
  mkdir -pv /var/www/letsencrypt/grafana && \
  nginx -t
