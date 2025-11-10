# Verolux Enterprise - Kubernetes Deployment Guide

## Overview

Deploy Verolux Enterprise on Google Kubernetes Engine (GKE) with full GPU support and auto-scaling.

## Prerequisites

- GCP Project with billing enabled
- kubectl installed
- gcloud CLI configured
- Docker images pushed to GCR

## Quick Start

### 1. Create GKE Cluster with GPU Support

```bash
# Set variables
export PROJECT_ID="your-project-id"
export CLUSTER_NAME="verolux-cluster"
export REGION="asia-southeast2"
export ZONE="asia-southeast2-a"

# Create GPU node pool cluster
gcloud container clusters create ${CLUSTER_NAME} \
  --zone=${ZONE} \
  --num-nodes=3 \
  --machine-type=n1-standard-4 \
  --enable-autoscaling \
  --min-nodes=2 \
  --max-nodes=10 \
  --enable-autorepair \
  --enable-autoupgrade \
  --scopes=https://www.googleapis.com/auth/cloud-platform

# Add GPU node pool
gcloud container node-pools create gpu-pool \
  --cluster=${CLUSTER_NAME} \
  --zone=${ZONE} \
  --accelerator=type=nvidia-l4,count=1 \
  --machine-type=g2-standard-8 \
  --num-nodes=1 \
  --min-nodes=1 \
  --max-nodes=3 \
  --enable-autoscaling \
  --enable-autorepair \
  --enable-autoupgrade \
  --scopes=https://www.googleapis.com/auth/cloud-platform

# Install NVIDIA GPU drivers
kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/container-engine-accelerators/master/nvidia-driver-installer/cos/daemonset-preloaded-latest.yaml
```

### 2. Configure Secrets

```bash
# Create namespace
kubectl create namespace verolux

# Create secret with DB password
kubectl create secret generic verolux-secrets \
  --from-literal=db-password=YOUR_DB_PASSWORD \
  --from-file=gcp-key.json=/path/to/your/gcp-key.json \
  -n verolux
```

### 3. Update Configuration

Edit `verolux-complete.yaml`:
- Replace `YOUR_PROJECT_ID` with your GCP project ID
- Update domain name in Ingress section
- Adjust resource limits as needed

### 4. Deploy All Services

```bash
# Apply all resources
kubectl apply -f verolux-complete.yaml

# Check deployment status
kubectl get all -n verolux

# Watch pods starting
kubectl get pods -n verolux -w
```

### 5. Access the Application

```bash
# Get LoadBalancer IP
kubectl get service frontend -n verolux

# Or through Ingress
kubectl get ingress verolux-ingress -n verolux
```

## Architecture

### Services Deployed

1. **Backend (1 pod)** - GPU-enabled YOLO inference
2. **Analytics (2 pods)** - Scalable analytics service
3. **Reporting (2 pods)** - Report generation
4. **Semantic Search (2 pods)** - FAISS/CLIP search
5. **Incident Reports (2 pods)** - Multi-language reports
6. **Config API (2 pods)** - Configuration management
7. **Frontend (3 pods)** - React dashboard

### Auto-Scaling

- HPA configured for backend based on CPU/GPU usage
- Node auto-scaling enabled (2-10 nodes)
- GPU node pool: 1-3 nodes

## Monitoring

### View Logs

```bash
# All pods
kubectl logs -f -l app=verolux-backend -n verolux

# Specific service
kubectl logs -f deployment/verolux-analytics -n verolux

# Tail logs from all services
stern verolux -n verolux
```

### Check Resource Usage

```bash
# Pod metrics
kubectl top pods -n verolux

# Node metrics
kubectl top nodes

# GPU utilization
kubectl describe node <GPU_NODE_NAME> | grep nvidia
```

## Scaling

### Manual Scaling

```bash
# Scale backend
kubectl scale deployment verolux-backend --replicas=3 -n verolux

# Scale analytics
kubectl scale deployment verolux-analytics --replicas=5 -n verolux
```

### Auto-Scaling Configuration

HPA is pre-configured:
- Backend: 1-5 replicas (70% CPU, 80% GPU)
- Other services: Manual scaling

To add HPA for other services:

```bash
kubectl autoscale deployment verolux-analytics \
  --cpu-percent=70 \
  --min=2 \
  --max=10 \
  -n verolux
```

## Troubleshooting

### GPU Not Available

```bash
# Check GPU driver installation
kubectl get daemonset nvidia-gpu-device-plugin -n kube-system

# Verify GPU on node
kubectl get nodes -o yaml | grep -i nvidia
```

### Pod Startup Issues

```bash
# Describe pod
kubectl describe pod <POD_NAME> -n verolux

# Check events
kubectl get events -n verolux --sort-by='.lastTimestamp'
```

### Service Not Accessible

```bash
# Check service endpoints
kubectl get endpoints -n verolux

# Port forward for testing
kubectl port-forward svc/backend 8000:8000 -n verolux
```

## Updating Deployment

### Update Image

```bash
# Build and push new image
docker build -t gcr.io/${PROJECT_ID}/verolux-backend:v2 .
docker push gcr.io/${PROJECT_ID}/verolux-backend:v2

# Update deployment
kubectl set image deployment/verolux-backend \
  backend=gcr.io/${PROJECT_ID}/verolux-backend:v2 \
  -n verolux

# Rollout status
kubectl rollout status deployment/verolux-backend -n verolux
```

### Rollback

```bash
# View history
kubectl rollout history deployment/verolux-backend -n verolux

# Rollback to previous
kubectl rollout undo deployment/verolux-backend -n verolux

# Rollback to specific revision
kubectl rollout undo deployment/verolux-backend --to-revision=3 -n verolux
```

## Cleanup

```bash
# Delete all resources
kubectl delete namespace verolux

# Delete cluster
gcloud container clusters delete ${CLUSTER_NAME} --zone=${ZONE}
```

## Cost Optimization

1. **Use Preemptible Nodes** (dev/test only):
```bash
gcloud container node-pools create preemptible-pool \
  --cluster=${CLUSTER_NAME} \
  --preemptible \
  --machine-type=n1-standard-4 \
  --num-nodes=2
```

2. **Auto-scaling**: Configured for all node pools

3. **Resource Requests**: Set appropriate limits to avoid over-provisioning

4. **Spot VMs**: Use for non-critical workloads (60-91% discount)

## Production Checklist

- [ ] SSL/TLS certificates configured
- [ ] Secrets stored in Secret Manager (not in Git)
- [ ] Resource limits properly set
- [ ] Health checks configured
- [ ] Monitoring and alerting setup
- [ ] Backup strategy implemented
- [ ] Network policies applied
- [ ] RBAC configured
- [ ] Auto-scaling tested
- [ ] Disaster recovery plan documented























