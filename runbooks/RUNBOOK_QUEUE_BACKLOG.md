# Runbook: Queue Backlog

## 🚨 Alert: RabbitMQ Queue Depth > 10,000

**Severity:** 🔴 Critical  
**Response Time:** 15 minutes  

## Symptoms
- Queue depth growing rapidly
- Task processing delays
- Celery workers overwhelmed
- Reports delayed

## Triage
```bash
# Check queue depth
curl http://localhost:15672/api/queues -u verolux:verolux123 | jq '.[].messages'

# Check worker status
curl http://localhost:5555/api/workers
```

## Resolution

### Immediate:
```bash
# 1. Scale up workers
docker-compose up -d --scale celery-worker=5

# 2. Pause non-critical tasks
# Stop celery-beat temporarily
docker-compose stop celery-beat
```

### Drain Queue:
```bash
# Process high-priority tasks only
celery -A celery_app purge -Q low-priority

# Monitor queue depth
watch -n 5 'curl -s http://localhost:15672/api/queues | jq ".[].messages"'
```

## Verification
Queue depth < 1,000 and decreasing

## Prevention
- Implement queue size limits
- Add backpressure handling
- Auto-scale workers based on queue depth



















