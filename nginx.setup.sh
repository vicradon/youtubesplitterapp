#!/usr/bin/env bash

sudo apt update \
&& sudo apt install nginx -y \
&& sudo snap install --classic certbot

servername=youtubedl.osinachi.me
port=14000

sudo touch /etc/nginx/conf.d/$servername.conf
sudo tee /etc/nginx/conf.d/$servername.conf > /dev/null <<EOF
server {
    listen 80;
    server_name $servername www.$servername;
    
    location / {
        proxy_pass http://localhost:$port;
    }
}
EOF

sudo nginx -t
sudo nginx -s reload

sudo certbot --nginx