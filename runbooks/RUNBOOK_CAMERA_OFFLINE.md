# Runbook: Camera Offline

## 🚨 **Alert**: Camera Offline > 10 Minutes

### **Severity**: 🔴 Critical  
**SLO Impact**: Camera Uptime (99.5%)  
**Response Time**: 15 minutes  

---

## 📋 **Symptoms**

- Alert: "Camera {camera_id} offline for 10+ minutes"
- Dashboard shows camera status: "dead" or "stale"
- No frames received from camera
- Reconnect attempts exhausted

---

## 🔍 **Triage**

### **Step 1: Check Camera Health**

```bash
# Get camera status
curl http://localhost:8000/health/cameras | jq '.cameras.gate_a1'

# Expected output:
# {
#   "is_healthy": false,
#   "status": "dead",
#   "last_frame_age_seconds": 650,
#   "reconnect_attempts": 10,
#   "error_message": "Connection refused"
# }
```

### **Step 2: Check Network Connectivity**

```bash
# Ping camera
ping -c 4 <camera-ip>

# Test RTSP port
telnet <camera-ip> 554
# OR
nc -zv <camera-ip> 554

# Expected: Connection successful or refused
```

### **Step 3: Check Camera Web Interface**

```bash
# Try accessing camera web UI
curl -I http://<camera-ip>

# Or open in browser
open http://<camera-ip>
```

---

## 🔧 **Resolution Steps**

### **Scenario A: Network Issue**

**Symptom:** Ping fails, no connectivity

**Actions:**
1. Check network cables
2. Check network switch status
3. Verify VLAN configuration
4. Check firewall rules (port 554 allowed)
5. Contact network team if needed

**Timeline:** 5-30 minutes

---

### **Scenario B: Camera Credentials Changed**

**Symptom:** Connection refused, authentication error

**Actions:**
1. Verify credentials in configuration
2. Try accessing camera web UI with same credentials
3. Reset camera password if needed
4. Update configuration:
   ```bash
   # Update camera config
   vi config/camera_config.json
   # Update: "username": "admin", "password": "newpass"
   ```
5. Restart backend to reload credentials

**Timeline:** 5-15 minutes

---

### **Scenario C: Camera Powered Off/Rebooting**

**Symptom:** No response, web UI inaccessible

**Actions:**
1. Check camera power LED
2. Check POE switch status
3. Power cycle camera if accessible
4. Wait for camera to boot (typically 2-5 minutes)
5. System will auto-reconnect once camera is back

**Timeline:** 5-10 minutes (mostly waiting)

---

### **Scenario D: Camera Firmware Issue**

**Symptom:** Camera accessible but RTSP not responding

**Actions:**
1. Access camera web UI
2. Check RTSP service status
3. Restart RTSP service from web UI
4. If not fixed, reboot camera
5. If still not fixed, consider firmware downgrade

**Timeline:** 10-30 minutes

---

### **Scenario E: RTSP URL Changed**

**Symptom:** Connection timeout, invalid stream path

**Actions:**
1. Access camera web UI
2. Check RTSP stream path
3. Update configuration with correct path:
   ```bash
   # Update RTSP URL
   # Old: rtsp://camera-ip/stream1
   # New: rtsp://camera-ip/Streaming/Channels/101
   ```
4. Restart backend

**Timeline:** 5 minutes

---

## ✅ **Verification**

After resolution:

```bash
# 1. Check camera status
curl http://localhost:8000/health/cameras | jq '.cameras.gate_a1.status'
# Expected: "healthy"

# 2. Check FPS
curl http://localhost:8000/health/cameras | jq '.cameras.gate_a1.current_fps'
# Expected: 25-30

# 3. Monitor for 5 minutes
watch -n 10 'curl -s http://localhost:8000/health/cameras | jq .cameras.gate_a1.status'
# Should stay "healthy"
```

---

## 📊 **Postmortem Template**

```markdown
## Camera Offline Incident

**Date:** YYYY-MM-DD HH:MM UTC
**Duration:** X minutes
**Camera:** {camera_id}
**Impact:** SLO breach (X% of error budget consumed)

### Root Cause:
[e.g., Network switch failure, camera power issue]

### Timeline:
- T+0: Alert triggered
- T+5: Investigation started
- T+15: Root cause identified
- T+20: Resolution applied
- T+25: Verified fixed

### Preventive Measures:
1. [Action item 1]
2. [Action item 2]

### SLO Impact:
- Budget consumed: X hours
- Budget remaining: Y hours
- Status: Within/Exceeded budget
```

---

## 🛠 **Permanent Fixes**

### **Reduce Future Occurrences:**

1. **Improve Network Reliability**
   - Redundant network paths
   - UPS for switches
   - Monitor switch health

2. **Camera Firmware Updates**
   - Keep cameras on stable firmware
   - Test updates in dev first

3. **Automated Recovery**
   - Already implemented! ✅
   - Auto-reconnect handles most cases
   - Should auto-recover in < 2 minutes

4. **Better Monitoring**
   - Add network latency monitoring
   - Add camera reboot detection
   - Alert on camera firmware changes

---

## 📞 **Escalation**

**If not resolved in 30 minutes:**

1. Page senior engineer
2. Contact camera vendor support (if under warranty)
3. Consider failing over to backup camera (if available)

**Emergency Contact:**
- Network Team: [contact info]
- Camera Vendor: [support number]
- On-call SRE: [pagerduty]

---

**Last Updated:** December 2024  
**Review Frequency:** After each incident  
**Owner:** SRE Team




















