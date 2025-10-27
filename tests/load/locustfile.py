"""
Locust load testing script for Verolux API

Run with:
    locust -f tests/load/locustfile.py --host=http://localhost:8000

Or with web UI:
    locust -f tests/load/locustfile.py --host=http://localhost:8000 --web-host=0.0.0.0
"""

import os
import random
import json
from locust import HttpUser, task, between, events
from locust.contrib.fasthttp import FastHttpUser
import base64


class VeroluxAPIUser(FastHttpUser):
    """
    Simulates a user interacting with the Verolux API.
    Uses FastHttpUser for better performance during load testing.
    """
    
    # Wait time between tasks (simulates user think time)
    wait_time = between(1, 3)
    
    # Test image data (small base64 encoded test image)
    test_image_base64 = None
    
    def on_start(self):
        """Called when a user starts - setup code here"""
        # Create a small test image
        self.test_image_base64 = self._create_test_image()
        
        # Optionally login if needed
        # self.client.post("/auth/login", json={"username": "test", "password": "test"})
    
    def _create_test_image(self):
        """Create a small test image for upload tests"""
        # In real scenario, load from file
        # For now, return a placeholder
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    
    @task(5)
    def health_check(self):
        """
        Health check endpoint - high frequency
        Weight: 5 (runs 5x more than weight-1 tasks)
        """
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "ok":
                    response.success()
                else:
                    response.failure(f"Health check failed: {data}")
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(3)
    def get_gate_stats(self):
        """
        Get gate statistics
        Weight: 3
        """
        self.client.get("/gate/stats", name="/gate/stats")
    
    @task(2)
    def get_gate_completions(self):
        """
        Get gate completions list
        Weight: 2
        """
        self.client.get("/gate/completions?limit=10", name="/gate/completions")
    
    @task(1)
    def detect_image(self):
        """
        Image detection endpoint - lower frequency (resource intensive)
        Weight: 1
        """
        # Simulate image upload
        files = {
            'file': ('test.jpg', self.test_image_base64, 'image/jpeg')
        }
        with self.client.post("/detect", files=files, catch_response=True, name="/detect") as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Detection failed with {response.status_code}")
    
    @task(1)
    def get_gate_config(self):
        """
        Get gate configuration
        Weight: 1
        """
        self.client.get("/gate/config", name="/gate/config")


class VeroluxAnalyticsUser(FastHttpUser):
    """
    Simulates a user interacting with the Analytics API.
    """
    
    host = "http://localhost:8002"
    wait_time = between(2, 5)
    
    @task(3)
    def get_dashboard_metrics(self):
        """Get dashboard metrics"""
        self.client.get("/analytics/dashboard", name="/analytics/dashboard")
    
    @task(2)
    def get_trends(self):
        """Get analytics trends"""
        params = {
            "start_date": "2024-10-01",
            "end_date": "2024-10-13",
            "metric": "detections"
        }
        self.client.get("/analytics/trends", params=params, name="/analytics/trends")
    
    @task(1)
    def get_heatmap(self):
        """Get heatmap data"""
        self.client.get("/analytics/heatmap", name="/analytics/heatmap")


class VeroluxReportingUser(FastHttpUser):
    """
    Simulates a user interacting with the Reporting API.
    """
    
    host = "http://localhost:8001"
    wait_time = between(3, 8)
    
    @task(5)
    def list_reports(self):
        """List available reports"""
        self.client.get("/reports/list?limit=20", name="/reports/list")
    
    @task(1)
    def generate_report(self):
        """Generate a new report (heavy operation)"""
        data = {
            "session_id": f"test_session_{random.randint(1, 1000)}",
            "language": random.choice(["en", "id", "zh"])
        }
        with self.client.post("/reports/generate", json=data, catch_response=True, name="/reports/generate") as response:
            if response.status_code in [200, 201, 202]:
                response.success()
            else:
                response.failure(f"Report generation failed: {response.status_code}")


class VeroluxSemanticSearchUser(FastHttpUser):
    """
    Simulates a user performing semantic searches.
    """
    
    host = "http://localhost:8003"
    wait_time = between(1, 4)
    
    search_queries = [
        "security incidents last week",
        "violations at gate A",
        "failed security checks",
        "person detection anomalies",
        "high risk events"
    ]
    
    @task
    def search(self):
        """Perform semantic search"""
        query = random.choice(self.search_queries)
        data = {
            "query": query,
            "limit": 10
        }
        self.client.post("/search", json=data, name="/search")


# Event handlers for custom statistics
@events.init.add_listener
def on_locust_init(environment, **kwargs):
    """Called when Locust starts"""
    print("🚀 Verolux Load Test Starting")
    print(f"   Target: {environment.host if hasattr(environment, 'host') else 'Multiple hosts'}")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when test starts"""
    print("📊 Load test begun - ramping up users")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when test stops"""
    print("✅ Load test completed")
    
    # Print summary statistics
    stats = environment.stats
    print("\n" + "="*60)
    print("LOAD TEST SUMMARY")
    print("="*60)
    print(f"Total requests: {stats.total.num_requests}")
    print(f"Total failures: {stats.total.num_failures}")
    print(f"Average response time: {stats.total.avg_response_time:.2f}ms")
    print(f"Min response time: {stats.total.min_response_time:.2f}ms")
    print(f"Max response time: {stats.total.max_response_time:.2f}ms")
    print(f"Requests per second: {stats.total.total_rps:.2f}")
    print(f"Failure rate: {(stats.total.num_failures/stats.total.num_requests*100 if stats.total.num_requests > 0 else 0):.2f}%")
    print("="*60)


# For running multiple user classes simultaneously
# Use: locust -f locustfile.py --host=http://localhost:8000 VeroluxAPIUser VeroluxAnalyticsUser














