# Runbook: GPU Saturation

## 🚨 Alert: GPU Utilization > 95% for 10 Minutes

**Severity:** 🔴 Critical  
**SLO Impact:** Inference Performance (25 FPS)  
**Response Time:** 15 minutes  

## Symptoms
- GPU utilization constantly > 95%
- FPS drops below 20
- Inference latency spikes
- Frame drops increasing

## Triage
```bash
# Check GPU status
nvidia-smi

# Check inference FPS
curl http://localhost:8000/status/production | jq '.system.current_fps'

# Check batch size
echo $BATCH_SIZE
```

## Resolution

### Immediate (Reduce Load):
```bash
# 1. Reduce batch size
export BATCH_SIZE=2
docker-compose restart backend

# 2. Reduce number of active cameras
# Temporarily disable non-critical cameras

# 3. Increase substream scale (lower resolution)
export SUBSTREAM_SCALE=0.7
docker-compose restart backend
```

### Short-term (Scale Up):
```bash
# Add second GPU instance
gcloud compute instances create verolux-gpu-2 \
  --machine-type=g2-standard-8 \
  --accelerator=type=nvidia-l4,count=1
```

### Long-term (Optimize):
- Switch to INT8 TensorRT model (if not already)
- Implement camera prioritization
- Add GPU auto-scaling

## Verification
```bash
nvidia-smi
# GPU utilization should be < 80%

curl http://localhost:8000/status/production | jq '.system.current_fps'
# FPS should be > 25
```

## Prevention
- Monitor GPU trends
- Set up predictive scaling (ML-based)
- Capacity planning for camera additions



















