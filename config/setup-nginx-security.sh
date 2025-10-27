#!/bin/bash
# Setup Nginx Security Features

set -e

echo "🔒 Setting up Nginx Security Features"
echo "======================================"

# Check if htpasswd is available
if ! command -v htpasswd &> /dev/null; then
    echo "📦 Installing apache2-utils for htpasswd..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y apache2-utils
    elif command -v yum &> /dev/null; then
        sudo yum install -y httpd-tools
    else
        echo "❌ Please install htpasswd manually"
        exit 1
    fi
fi

# Create .htpasswd file for admin tools
echo ""
echo "📝 Creating password file for admin tools"
echo "   (Grafana, Prometheus, RabbitMQ, etc.)"
echo ""

read -p "Enter username for admin access: " admin_user
htpasswd -c /etc/nginx/.htpasswd "$admin_user"

echo ""
echo "✅ Password file created: /etc/nginx/.htpasswd"

# Set proper permissions
sudo chmod 644 /etc/nginx/.htpasswd
sudo chown nginx:nginx /etc/nginx/.htpasswd

echo ""
echo "🔐 To enable authentication in Nginx config:"
echo "   Uncomment 'auth_basic' directives in:"
echo "   - /grafana/"
echo "   - /prometheus/"
echo "   - /rabbitmq/"
echo "   - /minio/"
echo "   - /flower/"
echo "   - /jaeger/"

# Create cache directory
echo ""
echo "📂 Creating cache directory..."
sudo mkdir -p /var/cache/nginx
sudo chown -R nginx:nginx /var/cache/nginx

# Create log directory
echo ""
echo "📝 Setting up log directory..."
sudo mkdir -p /var/log/nginx
sudo chown -R nginx:nginx /var/log/nginx

# Test Nginx configuration
echo ""
echo "🔍 Testing Nginx configuration..."
if sudo nginx -t; then
    echo "✅ Nginx configuration is valid"
    
    echo ""
    read -p "Reload Nginx to apply changes? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo nginx -s reload
        echo "✅ Nginx reloaded successfully"
    fi
else
    echo "❌ Nginx configuration has errors"
    exit 1
fi

echo ""
echo "======================================"
echo "✅ Nginx security setup complete!"
echo ""
echo "📊 Rate Limiting Zones Configured:"
echo "   - api_limit: 10 req/s (burst 20)"
echo "   - upload_limit: 2 req/s (burst 5)"
echo "   - auth_limit: 5 req/min (burst 3)"
echo "   - search_limit: 5 req/s (burst 10)"
echo "   - report_limit: 1 req/s (burst 3)"
echo "   - ws_limit: 5 req/s (burst 10)"
echo ""
echo "🔒 Security Headers Enabled:"
echo "   - X-XSS-Protection"
echo "   - X-Frame-Options"
echo "   - X-Content-Type-Options"
echo "   - Content-Security-Policy"
echo "   - Referrer-Policy"
echo ""
echo "📝 Next Steps:"
echo "   1. Update nginx.conf to use enhanced config"
echo "   2. Test rate limiting: curl -I http://localhost/api/health"
echo "   3. Enable SSL/TLS for production"
echo "   4. Configure fail2ban for additional protection"
echo ""














