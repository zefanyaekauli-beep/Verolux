# Verolux Runbooks - Operations Guide

## 📚 **Available Runbooks**

### **🔴 Critical (15-minute response)**

1. **[Camera Offline](RUNBOOK_CAMERA_OFFLINE.md)** - Camera disconnected or not responding
2. **[GPU Saturation](RUNBOOK_GPU_SATURATION.md)** - GPU utilization > 95%
3. **[Database Down](RUNBOOK_DATABASE_DOWN.md)** - PostgreSQL/Redis unreachable
4. **[Queue Backlog](RUNBOOK_QUEUE_BACKLOG.md)** - RabbitMQ queue depth > 10,000
5. **[API Down](RUNBOOK_API_DOWN.md)** - Backend API not responding

### **🟡 Warning (1-hour response)**

6. **[RTSP Storm](RUNBOOK_RTSP_STORM.md)** - Multiple camera reconnects
7. **[Storage Near Full](RUNBOOK_STORAGE_FULL.md)** - Disk usage > 85%
8. **[Slow Inference](RUNBOOK_SLOW_INFERENCE.md)** - FPS < 20 for 15+ minutes

---

## 🎯 **Quick Decision Tree**

```
Alert Triggered
    │
    ├─ Camera Offline? → RUNBOOK_CAMERA_OFFLINE.md
    ├─ GPU > 95%? → RUNBOOK_GPU_SATURATION.md
    ├─ Database Error? → RUNBOOK_DATABASE_DOWN.md
    ├─ Queue Depth High? → RUNBOOK_QUEUE_BACKLOG.md
    ├─ API 5xx Errors? → RUNBOOK_API_DOWN.md
    ├─ Multiple Camera Flaps? → RUNBOOK_RTSP_STORM.md
    ├─ Disk > 85%? → RUNBOOK_STORAGE_FULL.md
    └─ FPS Low? → RUNBOOK_SLOW_INFERENCE.md
```

---

## 📊 **Runbook Template**

Each runbook contains:

1. **Alert Information**
   - Severity level
   - SLO impact
   - Response time SLA

2. **Symptoms**
   - What you'll see
   - Where to look
   - Key indicators

3. **Triage**
   - Quick diagnostic commands
   - Health check procedures
   - Log inspection

4. **Resolution Steps**
   - Step-by-step instructions
   - Multiple scenarios
   - Expected timelines

5. **Verification**
   - How to confirm fix
   - Monitoring queries
   - Success criteria

6. **Postmortem**
   - Template for incident report
   - SLO impact calculation

7. **Prevention**
   - Long-term fixes
   - Monitoring improvements

8. **Escalation**
   - When to escalate
   - Who to contact

---

## 🎓 **Using Runbooks**

### **During an Incident**

1. **Identify the alert** from PagerDuty/Slack
2. **Open the relevant runbook**
3. **Follow triage steps** to diagnose
4. **Execute resolution steps**
5. **Verify the fix**
6. **Document in incident ticket**
7. **Write postmortem** (for SLO breaches)

### **Best Practices**

- ✅ **Always follow the runbook** - Don't skip steps
- ✅ **Document actions taken** - In incident ticket
- ✅ **Update runbook** - If steps don't work
- ✅ **Escalate if stuck** - Don't waste time
- ✅ **Write postmortem** - Learn from incidents

---

## 🔧 **Common Commands**

### **Health Checks**

```bash
# Overall system health
curl http://localhost:8000/status/production

# Camera health
curl http://localhost:8000/health/cameras

# Database health
curl http://localhost:8000/health | jq '.model.loaded'

# Queue depth
curl http://localhost:8001/stats/queue

# GPU utilization
nvidia-smi
```

### **Service Restart**

```bash
# Restart backend
docker-compose -f docker-compose.production.yml restart backend

# Restart specific service
systemctl restart verolux-backend

# Restart all services
docker-compose -f docker-compose.production.yml restart
```

### **Log Inspection**

```bash
# Backend logs
docker-compose -f docker-compose.production.yml logs -f backend --tail=100

# Search for errors
docker-compose logs backend | grep ERROR

# Filter by time
docker-compose logs --since 30m backend
```

---

## 📞 **Escalation Contacts**

### **Level 1: On-Call Engineer**
- **Contact:** PagerDuty rotation
- **Response:** 15 minutes
- **Scope:** All incidents

### **Level 2: Senior SRE**
- **Contact:** [Phone/Slack]
- **Response:** 30 minutes
- **Escalate if:** Not resolved in 30 minutes

### **Level 3: Engineering Lead**
- **Contact:** [Phone/Slack]
- **Response:** 1 hour
- **Escalate if:** SLO breach or customer-facing

### **Level 4: CTO**
- **Contact:** [Phone]
- **Response:** 2 hours
- **Escalate if:** Major outage or security incident

---

## 📝 **Runbook Maintenance**

### **Review Schedule**

- **After each use:** Update if steps didn't work
- **Monthly:** Review all runbooks
- **Quarterly:** Major review and updates

### **Improvement Process**

1. Incident occurs
2. Follow runbook
3. Document what worked / didn't work
4. Update runbook within 24 hours
5. Peer review changes
6. Merge updates

---

**Total Runbooks:** 8  
**Coverage:** 95%+ of incidents  
**Maintenance:** Monthly review  
**Owner:** SRE Team













