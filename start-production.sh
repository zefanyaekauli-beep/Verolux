#!/bin/bash

# Verolux Production Stack Startup Script
set -e

echo "============================================"
echo "   Verolux Production Stack"
echo "============================================"
echo ""
echo "Starting complete production infrastructure..."
echo ""
echo "Services included:"
echo "  - Backend API + Gate Security"
echo "  - Frontend (React)"
echo "  - Analytics + Reporting + Semantic Search"
echo "  - RabbitMQ (Message Queue)"
echo "  - Celery (Task Workers)"
echo "  - PostgreSQL (Database)"
echo "  - Redis (Cache)"
echo "  - Qdrant (Vector DB)"
echo "  - MinIO (Object Storage)"
echo "  - MediaMTX (Media Server)"
echo "  - Triton (AI Inference)"
echo "  - Prometheus + Grafana (Monitoring)"
echo "  - Loki + Promtail (Logging)"
echo "  - Jaeger (Tracing)"
echo "  - Keycloak (Auth)"
echo "  - Vault (Secrets)"
echo "  - coturn (WebRTC TURN)"
echo "  - Nginx (Reverse Proxy)"
echo ""

# Check Docker
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running"
    exit 1
fi

# Create directories
echo "📁 Creating directories..."
mkdir -p Backend/uploads Backend/models Backend/config Backend/snapshots Backend/incident_reports
mkdir -p config/grafana/dashboards config/grafana/datasources
mkdir -p triton-models backups ssl

# Start services
echo ""
echo "🐳 Starting Docker services..."
docker-compose -f docker-compose.production.yml up -d

# Wait for initialization
echo ""
echo "⏳ Waiting for services to initialize (30 seconds)..."
sleep 30

# Check status
echo ""
echo "📊 Checking service status..."
docker-compose -f docker-compose.production.yml ps

echo ""
echo "============================================"
echo "✅ Production Stack Started!"
echo "============================================"
echo ""
echo "🌐 Access URLs:"
echo ""
echo "  MAIN APPLICATION:"
echo "  - Frontend:              http://localhost"
echo "  - Backend API:           http://localhost/api"
echo "  - API Documentation:     http://localhost/api/docs"
echo ""
echo "  MONITORING & OBSERVABILITY:"
echo "  - Grafana Dashboards:    http://localhost/grafana (admin/verolux123)"
echo "  - Prometheus:            http://localhost/prometheus"
echo "  - Jaeger Tracing:        http://localhost/jaeger"
echo "  - Celery Flower:         http://localhost/flower"
echo ""
echo "  INFRASTRUCTURE:"
echo "  - RabbitMQ Management:   http://localhost/rabbitmq (verolux/verolux123)"
echo "  - MinIO Console:         http://localhost/minio (verolux/verolux123456)"
echo "  - Keycloak Admin:        http://localhost:8080 (admin/admin123)"
echo "  - Vault:                 http://localhost:8200 (token: root)"
echo ""
echo "📊 Useful Commands:"
echo "  - View logs:             docker-compose -f docker-compose.production.yml logs -f"
echo "  - Stop system:           docker-compose -f docker-compose.production.yml down"
echo "  - Restart service:       docker-compose -f docker-compose.production.yml restart [service]"
echo ""















