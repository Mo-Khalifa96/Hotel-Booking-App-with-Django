#!/bin/bash

#Exit on failure
set -e 

#Start nginx only 
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d nginx

#Renew SSL certificates
docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm certbot renew

#Reload nginx to apply renewed certificates
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec nginx nginx -s reload


#make sure to execute these two commands to schedule 
# the execution of this file periodically by cron:
#terminal:
# crontab -e  
# 0 0 * * * /path/to/renew.sh >> /var/log/certbot-renew.log 2>&1
