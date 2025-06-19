#!/bin/bash

#Exit on failure
set -e 

#Start nginx
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d nginx 

#Request SSL certificates 
docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot --webroot-path=/var/www/certbot \
  --email your-email@example.com \  #replace by actual email
  --agree-tos \
  --no-eff-email \
  -d your-domain.com -d www.your-domain.com   #replace with actual domain

#Reload nginx with the new certificates
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec nginx nginx -s reload


#Start entire dockerized application
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
