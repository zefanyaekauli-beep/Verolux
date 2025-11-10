/**
 * k6 Load Testing Script for Verolux API
 * 
 * Run with:
 *   k6 run tests/load/k6-script.js
 * 
 * Run with custom options:
 *   k6 run --vus 10 --duration 30s tests/load/k6-script.js
 * 
 * Run with cloud output:
 *   k6 run --out cloud tests/load/k6-script.js
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const healthCheckDuration = new Trend('health_check_duration');
const detectionDuration = new Trend('detection_duration');
const totalRequests = new Counter('total_requests');

// Test configuration
export const options = {
  stages: [
    // Ramp-up
    { duration: '30s', target: 10 },  // Ramp up to 10 users over 30s
    { duration: '1m', target: 20 },   // Ramp up to 20 users over 1 minute
    
    // Sustained load
    { duration: '2m', target: 20 },   // Stay at 20 users for 2 minutes
    
    // Peak load
    { duration: '30s', target: 50 },  // Spike to 50 users
    { duration: '1m', target: 50 },   // Hold at 50 users
    
    // Ramp-down
    { duration: '30s', target: 0 },   // Ramp down to 0 users
  ],
  
  thresholds: {
    // 95% of requests must complete within 2s
    'http_req_duration': ['p(95)<2000'],
    
    // Error rate must be less than 1%
    'errors': ['rate<0.01'],
    
    // 99% of requests must succeed
    'http_req_failed': ['rate<0.01'],
    
    // Health checks should be fast (95% under 500ms)
    'health_check_duration': ['p(95)<500'],
  },
};

// Base URLs
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const ANALYTICS_URL = __ENV.ANALYTICS_URL || 'http://localhost:8002';
const REPORTING_URL = __ENV.REPORTING_URL || 'http://localhost:8001';
const SEARCH_URL = __ENV.SEARCH_URL || 'http://localhost:8003';

// Test data
const searchQueries = [
  'security incidents last week',
  'violations at gate A',
  'failed security checks',
  'person detection anomalies',
  'high risk events'
];

export default function () {
  // Scenario 1: Health Check (High frequency - 40%)
  if (Math.random() < 0.4) {
    const healthRes = http.get(`${BASE_URL}/health`);
    
    const healthCheck = check(healthRes, {
      'health status is 200': (r) => r.status === 200,
      'health status is ok': (r) => JSON.parse(r.body).status === 'ok',
      'health response time < 500ms': (r) => r.timings.duration < 500,
    });
    
    healthCheckDuration.add(healthRes.timings.duration);
    errorRate.add(!healthCheck);
    totalRequests.add(1);
  }
  
  // Scenario 2: Gate Statistics (30%)
  else if (Math.random() < 0.7) {
    const statsRes = http.get(`${BASE_URL}/gate/stats`);
    
    check(statsRes, {
      'stats status is 200': (r) => r.status === 200,
      'stats has data': (r) => r.body.length > 0,
    });
    
    totalRequests.add(1);
  }
  
  // Scenario 3: Gate Completions (20%)
  else if (Math.random() < 0.9) {
    const completionsRes = http.get(`${BASE_URL}/gate/completions?limit=10`);
    
    check(completionsRes, {
      'completions status is 200': (r) => r.status === 200,
    });
    
    totalRequests.add(1);
  }
  
  // Scenario 4: Image Detection (10% - resource intensive)
  else {
    // Create a small test image (1x1 pixel PNG)
    const testImage = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==';
    
    const detectRes = http.post(
      `${BASE_URL}/detect`,
      {
        file: http.file(testImage, 'test.png', 'image/png')
      }
    );
    
    const detectCheck = check(detectRes, {
      'detection status is 200 or 202': (r) => r.status === 200 || r.status === 202,
    });
    
    detectionDuration.add(detectRes.timings.duration);
    errorRate.add(!detectCheck);
    totalRequests.add(1);
  }
  
  // Random sleep between 1-3 seconds to simulate user think time
  sleep(Math.random() * 2 + 1);
}

// Setup function - runs once before the test
export function setup() {
  console.log('🚀 Starting Verolux Load Test');
  console.log(`   Base URL: ${BASE_URL}`);
  console.log(`   Analytics URL: ${ANALYTICS_URL}`);
  console.log(`   Reporting URL: ${REPORTING_URL}`);
  console.log(`   Search URL: ${SEARCH_URL}`);
  
  // Verify API is accessible
  const healthCheck = http.get(`${BASE_URL}/health`);
  if (healthCheck.status !== 200) {
    throw new Error(`API health check failed: ${healthCheck.status}`);
  }
  
  return { startTime: new Date() };
}

// Teardown function - runs once after the test
export function teardown(data) {
  const endTime = new Date();
  const duration = (endTime - data.startTime) / 1000;
  
  console.log('\n' + '='.repeat(60));
  console.log('LOAD TEST COMPLETED');
  console.log('='.repeat(60));
  console.log(`Duration: ${duration.toFixed(2)}s`);
  console.log('Check k6 output above for detailed metrics');
  console.log('='.repeat(60));
}

// Analytics scenario - run separately
export function analyticsScenario() {
  const dashboardRes = http.get(`${ANALYTICS_URL}/analytics/dashboard`);
  check(dashboardRes, {
    'analytics dashboard status is 200': (r) => r.status === 200,
  });
  
  sleep(2);
}

// Search scenario - run separately
export function searchScenario() {
  const query = searchQueries[Math.floor(Math.random() * searchQueries.length)];
  
  const searchRes = http.post(
    `${SEARCH_URL}/search`,
    JSON.stringify({ query: query, limit: 10 }),
    { headers: { 'Content-Type': 'application/json' } }
  );
  
  check(searchRes, {
    'search status is 200': (r) => r.status === 200,
    'search returns results': (r) => JSON.parse(r.body).results !== undefined,
  });
  
  sleep(1);
}




















