# Production Deployment Guide

## Server Requirements

### 1. Install Required Services

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Redis
sudo apt install redis-server -y
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Install PostgreSQL with PostGIS
sudo apt install postgresql postgresql-contrib postgis postgresql-14-postgis-3 -y

# Install Python dependencies
sudo apt install python3-pip python3-venv python3-dev -y
sudo apt install build-essential libpq-dev -y

# Install GDAL for GeoDjango
sudo apt install gdal-bin libgdal-dev -y
```

### 2. Create Application User

```bash
# Create user for the application
sudo useradd -m -s /bin/bash zyra
sudo usermod -aG www-data zyra

# Create application directories
sudo mkdir -p /var/www/zyra.daraza.net
sudo mkdir -p /var/www/static
sudo mkdir -p /var/www/media
sudo mkdir -p /var/log/django

# Set permissions
sudo chown -R zyra:www-data /var/www/zyra.daraza.net
sudo chown -R zyra:www-data /var/www/static
sudo chown -R zyra:www-data /var/www/media
sudo chown -R zyra:www-data /var/log/django
```

### 3. Database Setup

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE db_zyra;
CREATE USER zyra_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE db_zyra TO zyra_user;
ALTER USER zyra_user CREATEDB;

# Enable PostGIS
\c db_zyra
CREATE EXTENSION postgis;
\q
```

### 4. Nginx Configuration

Create `/etc/nginx/sites-available/zyra.daraza.net`:

```nginx
# Rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name zyra.daraza.net www.zyra.daraza.net;
    return 301 https://$server_name$request_uri;
}

# Main HTTPS server
server {
    listen 443 ssl http2;
    server_name zyra.daraza.net www.zyra.daraza.net;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/zyra.daraza.net/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/zyra.daraza.net/privkey.pem;
    
    # SSL Security
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # Static files
    location /static/ {
        alias /var/www/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /var/www/media/;
        expires 1y;
        add_header Cache-Control "public";
    }

    # API rate limiting
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Login rate limiting
    location /accounts/login/ {
        limit_req zone=login burst=5 nodelay;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
    }

    # Main application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # WebSocket support
    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/zyra.daraza.net /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 5. SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d zyra.daraza.net -d www.zyra.daraza.net

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 6. Systemd Service for Django

Create `/etc/systemd/system/zyra.service`:

```ini
[Unit]
Description=zyra Django Application
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=zyra
Group=www-data
WorkingDirectory=/var/www/zyra.daraza.net
Environment=DJANGO_SETTINGS_MODULE=zyra.settings
Environment=PYTHONPATH=/var/www/zyra.daraza.net
ExecStart=/var/www/zyra.daraza.net/venv/bin/daphne -b 127.0.0.1 -p 8000 zyra.asgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable zyra
sudo systemctl start zyra
```

### 7. Celery Worker Service

Create `/etc/systemd/system/zyra-celery.service`:

```ini
[Unit]
Description=zyra Celery Worker
After=network.target redis.service

[Service]
Type=exec
User=zyra
Group=www-data
WorkingDirectory=/var/www/zyra.daraza.net
Environment=DJANGO_SETTINGS_MODULE=zyra.settings
ExecStart=/var/www/zyra.daraza.net/venv/bin/celery -A zyra worker -l info
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 8. Celery Beat Service

Create `/etc/systemd/system/zyra-celerybeat.service`:

```ini
[Unit]
Description=zyra Celery Beat
After=network.target redis.service

[Service]
Type=exec
User=zyra
Group=www-data
WorkingDirectory=/var/www/zyra.daraza.net
Environment=DJANGO_SETTINGS_MODULE=zyra.settings
ExecStart=/var/www/zyra.daraza.net/venv/bin/celery -A zyra beat -l info
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 9. Environment Variables

Create `/var/www/zyra.daraza.net/.env`:

```bash
# Django Settings
DEBUG=False
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=zyra.daraza.net,www.zyra.daraza.net

# Database
POSTGRES_DBNAME=db_zyra
POSTGRES_USER=zyra_user
POSTGRES_PASS=your_secure_password
PG_HOST=localhost
PG_PORT=5432

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@zyra.daraza.net
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=noreply@zyra.daraza.net

# Google OAuth
GOOGLE_OAUTH_CLIENT_ID=your_production_google_client_id
GOOGLE_OAUTH_CLIENT_SECRET=your_production_google_client_secret

# Apple OAuth
APPLE_OAUTH_CLIENT_ID=com.zyra.web.service
APPLE_OAUTH_CLIENT_SECRET=your_production_client_secret
APPLE_OAUTH_KEY_ID=your_apple_key_id
APPLE_OAUTH_PRIVATE_KEY=your_apple_private_key

# Google Maps
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
```

### 10. Deployment Commands

```bash
# Switch to application user
sudo su - zyra

# Navigate to application directory
cd /var/www/zyra.daraza.net

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser

# Restart services
sudo systemctl restart zyra
sudo systemctl restart zyra-celery
sudo systemctl restart zyra-celerybeat
sudo systemctl restart nginx
```

### 11. Monitoring and Logs

```bash
# Check service status
sudo systemctl status zyra
sudo systemctl status zyra-celery
sudo systemctl status zyra-celerybeat
sudo systemctl status nginx
sudo systemctl status redis-server
sudo systemctl status postgresql

# View logs
sudo journalctl -u zyra -f
sudo journalctl -u zyra-celery -f
sudo journalctl -u zyra-celerybeat -f
tail -f /var/log/django/zyra.log
tail -f /var/log/django/zyra_errors.log
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### 12. Security Checklist

- [ ] Change default admin URL in settings
- [ ] Use strong database passwords
- [ ] Enable firewall (ufw)
- [ ] Regular security updates
- [ ] Monitor logs for suspicious activity
- [ ] Backup database regularly
- [ ] Test SSL configuration
- [ ] Verify all security headers

### 13. Backup Strategy

```bash
# Database backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h localhost -U zyra_user db_zyra > /var/backups/zyra_db_$DATE.sql
gzip /var/backups/zyra_db_$DATE.sql

# Keep only last 7 days
find /var/backups -name "zyra_db_*.sql.gz" -mtime +7 -delete
```

Add to crontab:
```bash
0 2 * * * /path/to/backup_script.sh
```

This configuration provides a production-ready setup with security, performance, and monitoring capabilities.
