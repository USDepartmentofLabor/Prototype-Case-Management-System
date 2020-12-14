#!/bin/sh

# Environment Variables
# - UPSTREAM_FLASK_URL=www-flask:5000
# - UPSTREAM_ANGULAR_URL=www-angular:4200
# - UPSTREAM_METABASE_URL=metabase:3000
# - DOWNSTREAM_METABASE_URL=metabase.localhost
# - SERVER_URL=localhost

# Build nginx secure config

cat > /etc/nginx/conf.d/default.conf <<EOF
upstream flask {
    server ${UPSTREAM_FLASK_URL};
}

upstream angular {
    server ${UPSTREAM_ANGULAR_URL};
}

upstream metabase {
    server ${UPSTREAM_METABASE_URL};
}

server {
    listen 80;
    server_name ${SERVER_URL};
    
    location / {
        proxy_redirect off;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_pass http://flask;
    }
}

server {
    listen 80;
    server_name ${WEBAPP_URL};

    location / {
        proxy_redirect off;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_pass http://angular;
    }
}

server {
    listen 80;
    server_name ${DOWNSTREAM_METABASE_URL};

    location / {
        proxy_redirect off;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_pass http://metabase;
    }
}
EOF

# Build nginx main config

cat > /etc/nginx/nginx.conf <<EOF
user nginx;
worker_processes 1;

error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    access_log /var/log/nginx/access.log combined;
    sendfile on;
    keepalive_timeout 65;
    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
EOF

# End of Docker ENTRYPOINT
# Beginning of Docker CMD
nginx -g 'daemon off;'
