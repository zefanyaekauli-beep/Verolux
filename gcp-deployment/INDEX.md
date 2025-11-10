# Verolux Enterprise - GCP Deployment File Index

## 📂 Directory Structure

```
gcp-deployment/
├── docker/               # Docker container definitions
├── terraform/           # Infrastructure as Code
├── kubernetes/          # Kubernetes manifests
├── scripts/            # Automation scripts
├── config/             # Configuration files
└── INDEX.md            # This file
```

---

## 🐳 Docker Files

### Backend Services
| File | Service | Port | Purpose |
|------|---------|------|---------|
| `docker/Dockerfile.backend` | Main Backend | 8000 | YOLO inference + API + WebSocket + Gate SOP |
| `docker/Dockerfile.analytics` | Analytics | 8002 | Traffic flow, behavior, heatmaps |
| `docker/Dockerfile.reporting` | Reporting | 8001 | PDF/CSV reports generation |
| `docker/Dockerfile.semantic` | Semantic Search | 8003 | FAISS + CLIP video search |
| `docker/Dockerfile.incident` | Incident Reports | 8004 | Multi-language incident PDFs |
| `docker/Dockerfile.config` | Config API | 8005 | Gate rules & system config |
| `docker/Dockerfile.frontend` | Frontend | 80/443 | React dashboard + Nginx |

---

## 🏗️ Terraform Infrastructure

| File | Purpose |
|------|---------|
| `terraform/main.tf` | Main infrastructure definition (Compute, Storage, Database, Networking) |
| `terraform/variables.tf` | Input variables (customizable parameters) |
| `terraform/terraform.tfvars.example` | Configuration template |

### Resources Created
- Compute Engine GPU instance (g2-standard-8 + L4)
- Cloud Storage bucket with lifecycle rules
- Cloud SQL PostgreSQL (15)
- VPC firewall rules
- Service accounts & IAM
- Secret Manager integration
- Cloud Monitoring alerts

---

## ☸️ Kubernetes Deployment

| File | Purpose |
|------|---------|
| `kubernetes/verolux-complete.yaml` | Complete K8s deployment (all 7 services) |
| `kubernetes/README.md` | Kubernetes deployment guide |

### K8s Resources
- Namespace: `verolux`
- Deployments: 7 (backend, analytics, reporting, semantic, incident, config, frontend)
- Services: 7 (ClusterIP) + 1 LoadBalancer
- ConfigMaps & Secrets
- PersistentVolumeClaim
- Ingress with HTTPS
- HorizontalPodAutoscaler

---

## 🔧 Configuration Files

| File | Purpose |
|------|---------|
| `config/nginx.conf` | Nginx main configuration |
| `config/default.conf` | Server blocks & API proxy |
| `config/storage-lifecycle.json` | GCS lifecycle rules (30→90 day retention) |
| `config/supervisord.conf` | Process manager for all services |

### Nginx Features
- WebSocket support
- API reverse proxy
- Rate limiting
- Gzip compression
- SSL/TLS ready
- Health checks

---

## 🛠️ Automation Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/deploy-to-gcp.sh` | Main deployment automation | `./deploy-to-gcp.sh` |
| `scripts/setup-secrets.sh` | Secret Manager configuration | `./setup-secrets.sh` |
| `scripts/startup-script.sh` | VM startup automation | Auto-runs on instance boot |
| `scripts/health-check.sh` | Service health monitoring | `./health-check.sh` |

### What Each Script Does

#### deploy-to-gcp.sh
1. Configures GCP project
2. Enables required APIs
3. Creates Cloud Storage bucket
4. Sets up Cloud SQL database
5. Creates service account
6. Builds & pushes Docker images
7. Creates GPU compute instance
8. Configures firewall rules
9. Sets up secrets

#### setup-secrets.sh
- Creates all secrets in Secret Manager
- Configures database credentials
- Stores Firebase config
- Saves Telegram/Email tokens
- Generates service account keys

#### startup-script.sh
- Installs Docker & nvidia-docker
- Pulls latest images from GCR
- Starts all services via docker-compose
- Configures auto-restart on reboot

#### health-check.sh
- Checks all 7 services
- Verifies GPU availability
- Lists Docker containers
- Reports failures

---

## 📋 Quick Reference

### Deploy Everything
```bash
# Option 1: One-click (from project root)
./QUICK_START_GCP.sh  # or .bat for Windows

# Option 2: Manual
cd gcp-deployment/scripts
./deploy-to-gcp.sh

# Option 3: Terraform
cd gcp-deployment/terraform
terraform apply

# Option 4: Kubernetes
kubectl apply -f gcp-deployment/kubernetes/verolux-complete.yaml
```

### Check Status
```bash
# Health check
./gcp-deployment/scripts/health-check.sh

# View logs
gcloud compute ssh verolux-gpu-instance \
  --command="docker-compose logs -f"

# Check GPU
gcloud compute ssh verolux-gpu-instance \
  --command="nvidia-smi"
```

### Update Deployment
```bash
# Rebuild images
docker-compose -f docker-compose.gcp.yml build

# Push to GCR
docker-compose -f docker-compose.gcp.yml push

# Restart services
gcloud compute ssh verolux-gpu-instance \
  --command="cd /opt/verolux && docker-compose pull && docker-compose up -d"
```

---

## 🔗 File Dependencies

### Core Dependencies
```
QUICK_START_GCP.sh
├── .env.gcp.example
├── docker-compose.gcp.yml
└── gcp-deployment/scripts/deploy-to-gcp.sh
    ├── gcp-deployment/docker/* (all Dockerfiles)
    ├── gcp-deployment/config/* (all configs)
    └── gcp-deployment/scripts/setup-secrets.sh
```

### Terraform Dependencies
```
terraform/main.tf
├── terraform/variables.tf
├── terraform/terraform.tfvars
└── scripts/startup-script.sh
```

### Kubernetes Dependencies
```
kubernetes/verolux-complete.yaml
├── ConfigMap (inline)
├── Secrets (create manually)
└── Docker images (pre-pushed to GCR)
```

---

## 📦 What Each Component Provides

### Docker Files → Container Images
- Isolated, portable service containers
- GPU support (backend only)
- Optimized for production
- Multi-stage builds for size reduction

### Terraform → Infrastructure
- Reproducible infrastructure
- Version-controlled config
- Automatic resource creation
- Cost-optimized settings

### Kubernetes → Orchestration
- Auto-scaling
- Load balancing
- Self-healing
- Rolling updates
- Resource management

### Scripts → Automation
- One-command deployment
- Consistent setup
- Error handling
- Status monitoring

### Config Files → Customization
- Nginx routing
- Storage policies
- Process management
- Performance tuning

---

## 🎯 Choose Your Deployment Method

### Method 1: Compute Engine (Recommended for 1-3 instances)
**Use**: `scripts/deploy-to-gcp.sh`
- ✅ Simplest setup
- ✅ Direct GPU access
- ✅ Full control
- ⚠️ Manual scaling

### Method 2: Terraform (Recommended for IaC)
**Use**: `terraform/main.tf`
- ✅ Infrastructure as Code
- ✅ Version controlled
- ✅ Reproducible
- ✅ Team collaboration

### Method 3: Kubernetes (Recommended for 5+ instances)
**Use**: `kubernetes/verolux-complete.yaml`
- ✅ Auto-scaling
- ✅ Self-healing
- ✅ Load balancing
- ✅ Rolling updates

---

## 📞 Support & Troubleshooting

### File Locations for Common Issues

**Docker build fails:**
- Check: `docker/Dockerfile.*`
- Fix: Update base images or dependencies

**Service won't start:**
- Check: `config/supervisord.conf` or `kubernetes/verolux-complete.yaml`
- Fix: Review environment variables

**Nginx errors:**
- Check: `config/nginx.conf` and `config/default.conf`
- Fix: Update proxy settings or ports

**Deployment fails:**
- Check: `scripts/deploy-to-gcp.sh`
- Fix: Verify GCP permissions and quotas

**Terraform errors:**
- Check: `terraform/variables.tf`
- Fix: Update terraform.tfvars with correct values

---

## 📊 File Size Reference

| Category | Files | Total Size (approx) |
|----------|-------|---------------------|
| Docker | 7 files | ~30 KB |
| Terraform | 3 files | ~25 KB |
| Kubernetes | 2 files | ~20 KB |
| Scripts | 4 files | ~25 KB |
| Config | 4 files | ~15 KB |
| **Total** | **20 files** | **~115 KB** |

---

## ✅ Completeness Checklist

- [x] All 7 service Dockerfiles created
- [x] Complete Terraform infrastructure
- [x] Full Kubernetes manifests
- [x] All automation scripts
- [x] All configuration files
- [x] Deployment documentation
- [x] Quick start guides
- [x] This index file

**Status: 100% Complete** ✅

Every file is ready for production deployment with zero feature loss!
























