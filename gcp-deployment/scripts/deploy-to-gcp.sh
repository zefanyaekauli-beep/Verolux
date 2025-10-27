#!/bin/bash
# Verolux Enterprise - Complete GCP Deployment Script
# Deploys all 7 services with full feature preservation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration - Set these or use environment variables
PROJECT_ID=${GCP_PROJECT_ID:-"your-project-id"}
REGION=${GCP_REGION:-"asia-southeast2"}
ZONE=${GCP_ZONE:-"asia-southeast2-a"}
INSTANCE_NAME=${INSTANCE_NAME:-"verolux-gpu-instance"}
MACHINE_TYPE=${MACHINE_TYPE:-"g2-standard-8"}
GPU_TYPE=${GPU_TYPE:-"nvidia-l4"}
GPU_COUNT=${GPU_COUNT:-1}
DISK_SIZE=${DISK_SIZE:-"100"}

echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  🚀 Verolux Enterprise - GCP Deployment   ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""

# Check prerequisites
echo -e "${BLUE}📋 Checking prerequisites...${NC}"

if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Google Cloud SDK not found!${NC}"
    echo "Please install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found!${NC}"
    echo "Please install Docker"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"
echo ""

# Step 1: Configure GCP project
echo -e "${YELLOW}🔧 Step 1/10: Configuring GCP project...${NC}"
gcloud config set project ${PROJECT_ID}
gcloud config set compute/region ${REGION}
gcloud config set compute/zone ${ZONE}
echo -e "${GREEN}✅ Project configured: ${PROJECT_ID}${NC}"
echo ""

# Step 2: Enable required APIs
echo -e "${YELLOW}🔧 Step 2/10: Enabling required APIs...${NC}"
gcloud services enable compute.googleapis.com \
    storage-api.googleapis.com \
    sqladmin.googleapis.com \
    secretmanager.googleapis.com \
    containerregistry.googleapis.com \
    cloudbuild.googleapis.com \
    monitoring.googleapis.com \
    logging.googleapis.com \
    cloudresourcemanager.googleapis.com
echo -e "${GREEN}✅ APIs enabled${NC}"
echo ""

# Step 3: Create Cloud Storage bucket
echo -e "${YELLOW}💾 Step 3/10: Creating Cloud Storage bucket...${NC}"
BUCKET_NAME="${PROJECT_ID}-verolux-storage"
gsutil mb -p ${PROJECT_ID} -c STANDARD -l ${REGION} gs://${BUCKET_NAME}/ 2>/dev/null || true
gsutil lifecycle set gcp-deployment/config/storage-lifecycle.json gs://${BUCKET_NAME}/ 2>/dev/null || true
echo -e "${GREEN}✅ Storage bucket created: ${BUCKET_NAME}${NC}"
echo ""

# Step 4: Create Cloud SQL instance
echo -e "${YELLOW}🗄️  Step 4/10: Creating Cloud SQL PostgreSQL instance...${NC}"
gcloud sql instances create verolux-db \
    --database-version=POSTGRES_15 \
    --tier=db-custom-2-7680 \
    --region=${REGION} \
    --network=default \
    --database-flags=max_connections=200 \
    --backup-start-time=03:00 \
    --enable-bin-log \
    --retained-backups-count=7 2>/dev/null || true

# Create databases
gcloud sql databases create verolux_enterprise --instance=verolux-db 2>/dev/null || true
gcloud sql databases create verolux_analytics --instance=verolux-db 2>/dev/null || true

# Set root password
DB_PASSWORD=$(openssl rand -base64 32)
gcloud sql users set-password postgres \
    --instance=verolux-db \
    --password=${DB_PASSWORD} 2>/dev/null || true

echo -e "${GREEN}✅ Cloud SQL instance created${NC}"
echo ""

# Step 5: Create service account
echo -e "${YELLOW}🔐 Step 5/10: Creating service account...${NC}"
gcloud iam service-accounts create verolux-sa \
    --display-name="Verolux Service Account" 2>/dev/null || true

# Grant necessary roles
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:verolux-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin" 2>/dev/null || true

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:verolux-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/cloudsql.client" 2>/dev/null || true

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:verolux-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor" 2>/dev/null || true

echo -e "${GREEN}✅ Service account created and configured${NC}"
echo ""

# Step 6: Build Docker images
echo -e "${YELLOW}🐳 Step 6/10: Building Docker images...${NC}"
echo "Building backend (main + YOLO)..."
docker build -f gcp-deployment/docker/Dockerfile.backend -t gcr.io/${PROJECT_ID}/verolux-backend:latest .

echo "Building analytics..."
docker build -f gcp-deployment/docker/Dockerfile.analytics -t gcr.io/${PROJECT_ID}/verolux-analytics:latest .

echo "Building reporting..."
docker build -f gcp-deployment/docker/Dockerfile.reporting -t gcr.io/${PROJECT_ID}/verolux-reporting:latest .

echo "Building semantic search..."
docker build -f gcp-deployment/docker/Dockerfile.semantic -t gcr.io/${PROJECT_ID}/verolux-semantic:latest .

echo "Building incident reports..."
docker build -f gcp-deployment/docker/Dockerfile.incident -t gcr.io/${PROJECT_ID}/verolux-incident:latest .

echo "Building config API..."
docker build -f gcp-deployment/docker/Dockerfile.config -t gcr.io/${PROJECT_ID}/verolux-config:latest .

echo "Building frontend..."
docker build -f gcp-deployment/docker/Dockerfile.frontend -t gcr.io/${PROJECT_ID}/verolux-frontend:latest .

echo -e "${GREEN}✅ All Docker images built${NC}"
echo ""

# Step 7: Push images to GCR
echo -e "${YELLOW}📤 Step 7/10: Pushing images to Google Container Registry...${NC}"
docker push gcr.io/${PROJECT_ID}/verolux-backend:latest
docker push gcr.io/${PROJECT_ID}/verolux-analytics:latest
docker push gcr.io/${PROJECT_ID}/verolux-reporting:latest
docker push gcr.io/${PROJECT_ID}/verolux-semantic:latest
docker push gcr.io/${PROJECT_ID}/verolux-incident:latest
docker push gcr.io/${PROJECT_ID}/verolux-config:latest
docker push gcr.io/${PROJECT_ID}/verolux-frontend:latest
echo -e "${GREEN}✅ All images pushed to GCR${NC}"
echo ""

# Step 8: Create GPU compute instance
echo -e "${YELLOW}🖥️  Step 8/10: Creating GPU compute instance...${NC}"
gcloud compute instances create ${INSTANCE_NAME} \
    --zone=${ZONE} \
    --machine-type=${MACHINE_TYPE} \
    --accelerator=type=${GPU_TYPE},count=${GPU_COUNT} \
    --image-family=pytorch-latest-gpu \
    --image-project=deeplearning-platform-release \
    --boot-disk-size=${DISK_SIZE}GB \
    --boot-disk-type=pd-ssd \
    --maintenance-policy=TERMINATE \
    --metadata-from-file=startup-script=gcp-deployment/scripts/startup-script.sh \
    --service-account=verolux-sa@${PROJECT_ID}.iam.gserviceaccount.com \
    --scopes=https://www.googleapis.com/auth/cloud-platform \
    --tags=verolux,http-server,https-server 2>/dev/null || true

echo -e "${GREEN}✅ GPU instance created${NC}"
echo ""

# Step 9: Configure firewall rules
echo -e "${YELLOW}🔥 Step 9/10: Configuring firewall rules...${NC}"
gcloud compute firewall-rules create verolux-http \
    --allow=tcp:80,tcp:443 \
    --target-tags=http-server,https-server \
    --source-ranges=0.0.0.0/0 \
    --description="Allow HTTP/HTTPS traffic" 2>/dev/null || true

gcloud compute firewall-rules create verolux-api \
    --allow=tcp:8000-8005 \
    --target-tags=verolux \
    --source-ranges=0.0.0.0/0 \
    --description="Allow API traffic" 2>/dev/null || true

gcloud compute firewall-rules create verolux-ssh \
    --allow=tcp:22 \
    --target-tags=verolux \
    --source-ranges=0.0.0.0/0 \
    --description="Allow SSH access" 2>/dev/null || true

echo -e "${GREEN}✅ Firewall rules configured${NC}"
echo ""

# Step 10: Setup secrets
echo -e "${YELLOW}🔐 Step 10/10: Setting up secrets...${NC}"
./gcp-deployment/scripts/setup-secrets.sh
echo -e "${GREEN}✅ Secrets configured${NC}"
echo ""

# Get instance external IP
echo -e "${BLUE}🌐 Getting instance IP address...${NC}"
sleep 5
EXTERNAL_IP=$(gcloud compute instances describe ${INSTANCE_NAME} \
    --zone=${ZONE} \
    --format='get(networkInterfaces[0].accessConfigs[0].natIP)')

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║        ✅ DEPLOYMENT SUCCESSFUL! ✅         ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📍 Instance Information:${NC}"
echo -e "   Name:     ${INSTANCE_NAME}"
echo -e "   Zone:     ${ZONE}"
echo -e "   IP:       ${EXTERNAL_IP}"
echo -e "   GPU:      ${GPU_COUNT}x ${GPU_TYPE}"
echo ""
echo -e "${BLUE}🌐 Access URLs (will be available in ~2-3 minutes):${NC}"
echo -e "   ${GREEN}Frontend:${NC}      http://${EXTERNAL_IP}"
echo -e "   ${GREEN}Backend API:${NC}   http://${EXTERNAL_IP}:8000"
echo -e "   ${GREEN}Analytics:${NC}     http://${EXTERNAL_IP}:8002"
echo -e "   ${GREEN}Reporting:${NC}     http://${EXTERNAL_IP}:8001"
echo -e "   ${GREEN}Semantic:${NC}      http://${EXTERNAL_IP}:8003"
echo -e "   ${GREEN}Incident:${NC}      http://${EXTERNAL_IP}:8004"
echo -e "   ${GREEN}Config:${NC}        http://${EXTERNAL_IP}:8005"
echo ""
echo -e "${BLUE}📝 Useful Commands:${NC}"
echo -e "   ${YELLOW}SSH to instance:${NC}"
echo -e "   gcloud compute ssh ${INSTANCE_NAME} --zone=${ZONE}"
echo ""
echo -e "   ${YELLOW}View logs:${NC}"
echo -e "   gcloud compute ssh ${INSTANCE_NAME} --zone=${ZONE} --command='docker-compose -f docker-compose.gcp.yml logs -f'"
echo ""
echo -e "   ${YELLOW}Check status:${NC}"
echo -e "   gcloud compute ssh ${INSTANCE_NAME} --zone=${ZONE} --command='docker ps'"
echo ""
echo -e "   ${YELLOW}Health check:${NC}"
echo -e "   curl http://${EXTERNAL_IP}:8000/health"
echo ""
echo -e "${BLUE}💰 Estimated Monthly Cost:${NC} Rp 20-28 jt (~\$1,300-1,800 USD)"
echo ""
echo -e "${YELLOW}⚠️  Note: Wait 2-3 minutes for all services to start${NC}"
echo ""

















