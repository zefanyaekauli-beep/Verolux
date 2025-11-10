# Verolux Load Testing

Comprehensive load testing suite for the Verolux AI surveillance system.

## Tools Included

### 1. **Locust** (Python-based)
- Easy to write tests in Python
- Web-based UI for real-time monitoring
- Distributed load generation
- Great for complex scenarios

### 2. **k6** (JavaScript-based)
- High performance, written in Go
- Scripting in JavaScript
- Built-in thresholds and metrics
- Cloud integration available

## Prerequisites

### Install Locust
```bash
pip install locust
```

### Install k6
**Windows (via Chocolatey):**
```bash
choco install k6
```

**Linux:**
```bash
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6
```

**macOS (via Homebrew):**
```bash
brew install k6
```

## Running Load Tests

### Locust Tests

#### 1. Basic Load Test
```bash
# Start with web UI
locust -f tests/load/locustfile.py --host=http://localhost:8000

# Open browser: http://localhost:8089
# Configure number of users and spawn rate
```

#### 2. Headless Mode (No UI)
```bash
# Run with specific users and duration
locust -f tests/load/locustfile.py \
  --host=http://localhost:8000 \
  --users 50 \
  --spawn-rate 5 \
  --run-time 5m \
  --headless
```

#### 3. Test Specific User Class
```bash
# Test only API endpoints
locust -f tests/load/locustfile.py \
  --host=http://localhost:8000 \
  VeroluxAPIUser \
  --headless \
  --users 20 \
  --run-time 2m
```

#### 4. Distributed Load Testing
```bash
# On master machine
locust -f tests/load/locustfile.py --master

# On worker machines (multiple)
locust -f tests/load/locustfile.py --worker --master-host=<master-ip>
```

### k6 Tests

#### 1. Basic Load Test
```bash
# Default configuration (from script)
k6 run tests/load/k6-script.js
```

#### 2. Custom VUs and Duration
```bash
# 100 virtual users for 5 minutes
k6 run --vus 100 --duration 5m tests/load/k6-script.js
```

#### 3. With Environment Variables
```bash
# Test different environments
k6 run \
  --env BASE_URL=http://staging.verolux.com:8000 \
  --env ANALYTICS_URL=http://staging.verolux.com:8002 \
  tests/load/k6-script.js
```

#### 4. Output to InfluxDB
```bash
# For Grafana visualization
k6 run --out influxdb=http://localhost:8086/k6 tests/load/k6-script.js
```

#### 5. Cloud Test (k6 Cloud)
```bash
# Requires k6 Cloud account
k6 login cloud
k6 run --out cloud tests/load/k6-script.js
```

## Load Testing Scenarios

### Scenario 1: Normal Load (Baseline)
```bash
# Locust
locust -f tests/load/locustfile.py --host=http://localhost:8000 \
  --users 20 --spawn-rate 2 --run-time 10m --headless

# k6
k6 run --vus 20 --duration 10m tests/load/k6-script.js
```
**Purpose:** Establish baseline performance metrics

### Scenario 2: Peak Load (High Traffic)
```bash
# Locust
locust -f tests/load/locustfile.py --host=http://localhost:8000 \
  --users 100 --spawn-rate 10 --run-time 15m --headless

# k6
k6 run --vus 100 --duration 15m tests/load/k6-script.js
```
**Purpose:** Test system under expected peak load

### Scenario 3: Stress Test (Breaking Point)
```bash
# Gradually increase until failure
locust -f tests/load/locustfile.py --host=http://localhost:8000 \
  --users 500 --spawn-rate 50 --run-time 30m --headless
```
**Purpose:** Find system breaking point

### Scenario 4: Spike Test (Sudden Load)
```bash
# Quick ramp-up
locust -f tests/load/locustfile.py --host=http://localhost:8000 \
  --users 200 --spawn-rate 100 --run-time 5m --headless
```
**Purpose:** Test system resilience to sudden traffic spikes

### Scenario 5: Soak Test (Endurance)
```bash
# Long-running test
k6 run --vus 50 --duration 4h tests/load/k6-script.js
```
**Purpose:** Detect memory leaks and stability issues

## Performance Targets

### Expected Metrics

| Metric | Target | Good | Acceptable | Poor |
|--------|--------|------|------------|------|
| **Response Time (p95)** | <500ms | <500ms | <1000ms | >1000ms |
| **Response Time (p99)** | <1000ms | <1000ms | <2000ms | >2000ms |
| **Throughput** | >100 req/s | >100 | >50 | <50 |
| **Error Rate** | <1% | <1% | <5% | >5% |
| **Concurrent Users** | 50+ | 100+ | 50+ | <50 |

### Endpoint-Specific Targets

| Endpoint | p95 Response Time | Throughput |
|----------|-------------------|------------|
| `/health` | <100ms | >500 req/s |
| `/gate/stats` | <300ms | >200 req/s |
| `/gate/completions` | <500ms | >100 req/s |
| `/detect` | <2000ms | >20 req/s |
| `/search` | <800ms | >50 req/s |

## Monitoring During Tests

### 1. System Resources
```bash
# CPU and Memory
htop

# GPU (if applicable)
nvidia-smi -l 1

# Network
iftop
```

### 2. Application Metrics
- **Grafana Dashboards:** http://localhost:3000
- **Prometheus Metrics:** http://localhost:9090
- **Jaeger Traces:** http://localhost:16686

### 3. Logs
```bash
# Backend logs
docker logs -f verolux-backend

# All services
docker-compose logs -f
```

## Analysis & Reporting

### Locust Reports

After test completion, Locust generates:
- `locust_report.html` - Visual report
- CSV files with detailed statistics

Save reports:
```bash
locust -f tests/load/locustfile.py --host=http://localhost:8000 \
  --users 50 --run-time 10m --headless \
  --html=reports/load_test_$(date +%Y%m%d_%H%M%S).html \
  --csv=reports/load_test_$(date +%Y%m%d_%H%M%S)
```

### k6 Reports

Generate summary:
```bash
k6 run tests/load/k6-script.js --summary-export=reports/k6_summary.json
```

Export to JSON:
```bash
k6 run tests/load/k6-script.js --out json=reports/k6_results.json
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Load Test

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install k6
        run: |
          sudo gpg -k
          sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
          echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
          sudo apt-get update
          sudo apt-get install k6
      
      - name: Run load test
        run: |
          k6 run tests/load/k6-script.js \
            --out json=results.json \
            --summary-export=summary.json
      
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: load-test-results
          path: |
            results.json
            summary.json
```

## Troubleshooting

### Issue: High error rate
**Solution:**
- Check system resources (CPU, memory, GPU)
- Reduce number of virtual users
- Increase timeout values
- Check application logs

### Issue: Slow response times
**Solution:**
- Enable batch inference
- Use TensorRT optimizations
- Check database query performance
- Enable caching (Redis)

### Issue: Connection errors
**Solution:**
- Increase file descriptors: `ulimit -n 65535`
- Check network bandwidth
- Verify firewall rules

### Issue: Memory leaks
**Solution:**
- Run soak tests to identify
- Check for unclosed connections
- Monitor with Grafana
- Use profiling tools

## Best Practices

1. **Start Small:** Begin with low load and gradually increase
2. **Baseline First:** Establish performance baseline before optimizations
3. **Monitor Everything:** Watch CPU, memory, GPU, network during tests
4. **Test in Stages:** Ramp-up, steady state, peak, ramp-down
5. **Isolate Variables:** Test one change at a time
6. **Document Results:** Keep records of all test runs
7. **Test Regularly:** Automated daily/weekly load tests
8. **Realistic Scenarios:** Match production traffic patterns

## Additional Resources

- [Locust Documentation](https://docs.locust.io/)
- [k6 Documentation](https://k6.io/docs/)
- [Load Testing Best Practices](https://k6.io/docs/testing-guides/api-load-testing/)
- [Performance Testing Guide](https://martinfowler.com/articles/performance-testing.html)

## Next Steps

After load testing:
1. ✅ Identify bottlenecks
2. ✅ Optimize critical paths
3. ✅ Scale infrastructure
4. ✅ Implement caching
5. ✅ Enable CDN
6. ✅ Database optimization
7. ✅ Re-test and compare





















