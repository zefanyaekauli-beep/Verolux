@echo off
echo ============================================
echo    Verolux Production Stack
echo ============================================
echo.
echo Starting complete production infrastructure...
echo.
echo Services included:
echo   - Backend API + Gate Security
echo   - Frontend (React)
echo   - Analytics + Reporting + Semantic Search
echo   - RabbitMQ (Message Queue)
echo   - Celery (Task Workers)
echo   - PostgreSQL (Database)
echo   - Redis (Cache)
echo   - Qdrant (Vector DB)
echo   - MinIO (Object Storage)
echo   - MediaMTX (Media Server)
echo   - Triton (AI Inference - optional GPU)
echo   - Prometheus + Grafana (Monitoring)
echo   - Loki + Promtail (Logging)
echo   - Jaeger (Tracing)
echo   - Keycloak (Auth)
echo   - Vault (Secrets)
echo   - coturn (WebRTC TURN)
echo   - Nginx (Reverse Proxy)
echo.
echo Press any key to start or Ctrl+C to cancel...
pause >nul

echo.
echo 🐳 Starting Docker services...
docker-compose -f docker-compose.production.yml up -d

echo.
echo ⏳ Waiting for services to initialize (30 seconds)...
timeout /t 30 /nobreak

echo.
echo 📊 Checking service status...
docker-compose -f docker-compose.production.yml ps

echo.
echo ============================================
echo ✅ Production Stack Started!
echo ============================================
echo.
echo 🌐 Access URLs:
echo.
echo   MAIN APPLICATION:
echo   - Frontend:              http://localhost
echo   - Backend API:           http://localhost/api
echo   - API Documentation:     http://localhost/api/docs
echo.
echo   MONITORING & OBSERVABILITY:
echo   - Grafana Dashboards:    http://localhost/grafana (admin/verolux123)
echo   - Prometheus:            http://localhost/prometheus
echo   - Jaeger Tracing:        http://localhost/jaeger
echo   - Celery Flower:         http://localhost/flower
echo.
echo   INFRASTRUCTURE:
echo   - RabbitMQ Management:   http://localhost/rabbitmq (verolux/verolux123)
echo   - MinIO Console:         http://localhost/minio (verolux/verolux123456)
echo   - Keycloak Admin:        http://localhost:8080 (admin/admin123)
echo   - Vault:                 http://localhost:8200 (token: root)
echo.
echo   DIRECT PORT ACCESS:
echo   - Frontend:              http://localhost:5173
echo   - Backend:               http://localhost:8000
echo   - Analytics:             http://localhost:8002
echo   - Reporting:             http://localhost:8001
echo   - Prometheus:            http://localhost:9090
echo   - Grafana:               http://localhost:3000
echo   - RabbitMQ:              http://localhost:15672
echo   - MinIO:                 http://localhost:9001
echo.
echo 📊 Useful Commands:
echo   - View logs:             docker-compose -f docker-compose.production.yml logs -f
echo   - Stop system:           docker-compose -f docker-compose.production.yml down
echo   - Restart service:       docker-compose -f docker-compose.production.yml restart [service]
echo   - View metrics:          Open http://localhost/grafana
echo.
pause















