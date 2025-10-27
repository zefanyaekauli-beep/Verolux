#!/bin/bash
# Verolux Enterprise - Health Check Script

set -e

PROJECT_ID=${GCP_PROJECT_ID:-"your-project-id"}
INSTANCE_NAME=${INSTANCE_NAME:-"verolux-gpu-instance"}
ZONE=${GCP_ZONE:-"asia-southeast2-a"}

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🏥 Verolux Enterprise - Health Check"
echo "====================================="
echo ""

# Get instance IP
EXTERNAL_IP=$(gcloud compute instances describe ${INSTANCE_NAME} \
    --zone=${ZONE} \
    --format='get(networkInterfaces[0].accessConfigs[0].natIP)' 2>/dev/null)

if [ -z "$EXTERNAL_IP" ]; then
    echo -e "${RED}❌ Could not get instance IP${NC}"
    exit 1
fi

echo "Instance IP: ${EXTERNAL_IP}"
echo ""

# Check services
check_service() {
    local name=$1
    local port=$2
    local endpoint=$3
    
    echo -n "Checking ${name} (${port})... "
    
    if curl -f -s -o /dev/null -w "%{http_code}" "http://${EXTERNAL_IP}:${port}${endpoint}" | grep -q "200"; then
        echo -e "${GREEN}✅ OK${NC}"
        return 0
    else
        echo -e "${RED}❌ FAILED${NC}"
        return 1
    fi
}

# Check all services
FAILURES=0

check_service "Frontend" "80" "/" || ((FAILURES++))
check_service "Backend API" "8000" "/health" || ((FAILURES++))
check_service "Analytics" "8002" "/health" || ((FAILURES++))
check_service "Reporting" "8001" "/health" || ((FAILURES++))
check_service "Semantic Search" "8003" "/health" || ((FAILURES++))
check_service "Incident Reports" "8004" "/health" || ((FAILURES++))
check_service "Config API" "8005" "/health" || ((FAILURES++))

echo ""

# Check GPU
echo "Checking GPU..."
GPU_STATUS=$(gcloud compute ssh ${INSTANCE_NAME} --zone=${ZONE} --command="nvidia-smi --query-gpu=name,utilization.gpu,memory.used,memory.total --format=csv,noheader" 2>/dev/null || echo "GPU check failed")
echo "${GPU_STATUS}"
echo ""

# Check Docker containers
echo "Checking Docker containers..."
gcloud compute ssh ${INSTANCE_NAME} --zone=${ZONE} --command="docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'" 2>/dev/null
echo ""

# Summary
if [ $FAILURES -eq 0 ]; then
    echo -e "${GREEN}✅ All services are healthy!${NC}"
    exit 0
else
    echo -e "${RED}❌ ${FAILURES} service(s) failed health check${NC}"
    exit 1
fi

















