# Install packages
sudo apt update \
&& sudo apt install nginx -y \
&& sudo snap install --classic certbot

# Configure Node.js App
npm install pm2 -g
nodeappdir=nodeapp-$RANDOM
port=5600
servername=server1.osinachi.me
mkdir $nodeappdir && cd $nodeappdir
npm init -y
npm install express

cat >> index.js <<EOF
const express = require('express');

const app = express();
app.get('/', (req, res) => res.send('<h1>Hello from Express.js</h1>'));

app.listen($port, () => console.log('app running on http://localhost:$port'));
EOF

pm2 start index.js

# Configure Nginx
sudo touch /etc/nginx/conf.d/$(hostname).conf
sudo tee /etc/nginx/conf.d/$(hostname).conf > /dev/null <<EOF
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