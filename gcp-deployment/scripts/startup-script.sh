#!/bin/bash
# Verolux Enterprise - GCP VM Startup Script
# Automatically runs when instance starts

set -e

echo "🚀 Verolux Enterprise - Startup Script"
echo "========================================"
date

# Install Docker and Docker Compose if not present
if ! command -v docker &> /dev/null; then
    echo "📦 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    
    # Add user to docker group
    usermod -aG docker $USER || true
fi

if ! command -v docker-compose &> /dev/null; then
    echo "📦 Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Install nvidia-docker if not present
if ! dpkg -l | grep -q nvidia-docker2; then
    echo "🎮 Installing NVIDIA Docker..."
    distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
    curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | apt-key add -
    curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | tee /etc/apt/sources.list.d/nvidia-docker.list
    apt-get update && apt-get install -y nvidia-docker2
    systemctl restart docker
fi

# Get project metadata
PROJECT_ID=$(gcloud config get-value project)
ZONE=$(gcloud compute instances list --filter="name=$(hostname)" --format='value(zone)')

echo "📍 Instance: $(hostname)"
echo "📍 Project: ${PROJECT_ID}"
echo "📍 Zone: ${ZONE}"

# Create working directory
WORK_DIR="/opt/verolux"
mkdir -p ${WORK_DIR}
cd ${WORK_DIR}

# Get secrets from Secret Manager
echo "🔐 Retrieving secrets..."
DB_PASSWORD=$(gcloud secrets versions access latest --secret="verolux-db-password" 2>/dev/null || echo "")
DB_HOST=$(gcloud secrets versions access latest --secret="verolux-db-host" 2>/dev/null || echo "localhost")
STORAGE_BUCKET=$(gcloud secrets versions access latest --secret="verolux-storage-bucket" 2>/dev/null || echo "${PROJECT_ID}-verolux-storage")
FIREBASE_CONFIG=$(gcloud secrets versions access latest --secret="verolux-firebase-config" 2>/dev/null || echo "{}")

# Save service account key
gcloud secrets versions access latest --secret="verolux-gcp-service-key" > /opt/verolux/gcp-key.json 2>/dev/null || true

# Create docker-compose file
cat > docker-compose.gcp.yml <<'EOF'
version: '3.8'

services:
  backend:
    image: gcr.io/${PROJECT_ID}/verolux-backend:latest
    container_name: verolux-backend
    ports:
      - "8000:8000"
    environment:
      - MODEL_PATH=/app/models/weight.pt
      - DEVICE=cuda
      - BATCH_SIZE=4
      - SUBSTREAM_SCALE=0.6
      - DB_HOST=${DB_HOST}
      - DB_NAME=verolux_enterprise
      - DB_USER=postgres
      - DB_PASSWORD=${DB_PASSWORD}
      - GCS_BUCKET=${STORAGE_BUCKET}
      - GOOGLE_APPLICATION_CREDENTIALS=/secrets/gcp-key.json
    volumes:
      - /opt/verolux/gcp-key.json:/secrets/gcp-key.json:ro
      - backend-uploads:/app/uploads
      - backend-models:/app/models
    runtime: nvidia
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    networks:
      - verolux-network
    restart: unless-stopped

  analytics:
    image: gcr.io/${PROJECT_ID}/verolux-analytics:latest
    container_name: verolux-analytics
    ports:
      - "8002:8002"
    environment:
      - DB_HOST=${DB_HOST}
      - DB_NAME=verolux_analytics
      - DB_USER=postgres
      - DB_PASSWORD=${DB_PASSWORD}
      - GCS_BUCKET=${STORAGE_BUCKET}
      - GOOGLE_APPLICATION_CREDENTIALS=/secrets/gcp-key.json
    volumes:
      - /opt/verolux/gcp-key.json:/secrets/gcp-key.json:ro
    networks:
      - verolux-network
    restart: unless-stopped

  reporting:
    image: gcr.io/${PROJECT_ID}/verolux-reporting:latest
    container_name: verolux-reporting
    ports:
      - "8001:8001"
    environment:
      - DB_HOST=${DB_HOST}
      - DB_NAME=verolux_analytics
      - DB_USER=postgres
      - DB_PASSWORD=${DB_PASSWORD}
      - GCS_BUCKET=${STORAGE_BUCKET}
      - GOOGLE_APPLICATION_CREDENTIALS=/secrets/gcp-key.json
    volumes:
      - /opt/verolux/gcp-key.json:/secrets/gcp-key.json:ro
      - reports:/app/reports
    networks:
      - verolux-network
    restart: unless-stopped

  semantic:
    image: gcr.io/${PROJECT_ID}/verolux-semantic:latest
    container_name: verolux-semantic
    ports:
      - "8003:8003"
    environment:
      - DB_HOST=${DB_HOST}
      - DB_USER=postgres
      - DB_PASSWORD=${DB_PASSWORD}
      - GCS_BUCKET=${STORAGE_BUCKET}
      - GOOGLE_APPLICATION_CREDENTIALS=/secrets/gcp-key.json
    volumes:
      - /opt/verolux/gcp-key.json:/secrets/gcp-key.json:ro
      - semantic-embeddings:/app/embeddings
    networks:
      - verolux-network
    restart: unless-stopped

  incident:
    image: gcr.io/${PROJECT_ID}/verolux-incident:latest
    container_name: verolux-incident
    ports:
      - "8004:8004"
    environment:
      - DB_HOST=${DB_HOST}
      - DB_USER=postgres
      - DB_PASSWORD=${DB_PASSWORD}
      - GCS_BUCKET=${STORAGE_BUCKET}
      - GOOGLE_APPLICATION_CREDENTIALS=/secrets/gcp-key.json
    volumes:
      - /opt/verolux/gcp-key.json:/secrets/gcp-key.json:ro
      - incident-reports:/app/incident_reports
    networks:
      - verolux-network
    restart: unless-stopped

  config:
    image: gcr.io/${PROJECT_ID}/verolux-config:latest
    container_name: verolux-config
    ports:
      - "8005:8005"
    environment:
      - DB_HOST=${DB_HOST}
      - DB_USER=postgres
      - DB_PASSWORD=${DB_PASSWORD}
      - GCS_BUCKET=${STORAGE_BUCKET}
      - GOOGLE_APPLICATION_CREDENTIALS=/secrets/gcp-key.json
    volumes:
      - /opt/verolux/gcp-key.json:/secrets/gcp-key.json:ro
      - config-data:/app/config
    networks:
      - verolux-network
    restart: unless-stopped

  frontend:
    image: gcr.io/${PROJECT_ID}/verolux-frontend:latest
    container_name: verolux-frontend
    ports:
      - "80:80"
      - "443:443"
    environment:
      - VITE_API_URL=http://localhost:8000
      - VITE_WS_URL=ws://localhost:8000
    networks:
      - verolux-network
    restart: unless-stopped
    depends_on:
      - backend

volumes:
  backend-uploads:
  backend-models:
  reports:
  semantic-embeddings:
  incident-reports:
  config-data:

networks:
  verolux-network:
    driver: bridge
EOF

# Replace environment variables in docker-compose
export PROJECT_ID
export DB_HOST
export DB_PASSWORD
export STORAGE_BUCKET
envsubst < docker-compose.gcp.yml > docker-compose.yml

# Pull latest images
echo "📥 Pulling latest Docker images..."
docker-compose pull

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down 2>/dev/null || true

# Start services
echo "🚀 Starting all services..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to start..."
sleep 30

# Check service health
echo "🏥 Checking service health..."
docker-compose ps

# Show logs
echo "📋 Recent logs:"
docker-compose logs --tail=20

echo ""
echo "✅ Startup complete!"
echo "🌐 Access the system at: http://$(curl -s http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip -H "Metadata-Flavor: Google")"
echo ""

# Setup auto-restart on reboot
cat > /etc/systemd/system/verolux.service <<'SVCEOF'
[Unit]
Description=Verolux Enterprise Services
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/verolux
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
SVCEOF

systemctl daemon-reload
systemctl enable verolux.service

echo "✅ Auto-start configured"























