#!/usr/bin/env python3
"""
Celery Application for Verolux Background Tasks
Handles heavy tasks: video processing, report generation, data export
"""
import os
from celery import Celery
from celery.schedules import crontab

# Get broker URL from environment
BROKER_URL = os.getenv('RABBITMQ_URL', 'amqp://verolux:verolux123@localhost:5672')
BACKEND_URL = os.getenv('REDIS_URL', 'redis://:verolux123@localhost:6379/0')

# Create Celery app
app = Celery(
    'verolux',
    broker=BROKER_URL,
    backend=BACKEND_URL,
    include=[
        'tasks.video_processing',
        'tasks.report_generation',
        'tasks.data_export',
        'tasks.analytics_jobs'
    ]
)

# Configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Task routing
    task_routes={
        'tasks.video_processing.*': {'queue': 'heavy'},
        'tasks.report_generation.*': {'queue': 'reports'},
        'tasks.analytics_jobs.*': {'queue': 'default'},
        'tasks.data_export.*': {'queue': 'default'},
    },
    
    # Task time limits
    task_time_limit=3600,  # 1 hour hard limit
    task_soft_time_limit=3000,  # 50 minutes soft limit
    
    # Result backend settings
    result_expires=86400,  # 24 hours
    result_backend_transport_options={
        'master_name': 'verolux',
    },
    
    # Worker settings
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    
    # Beat schedule (periodic tasks)
    beat_schedule={
        'cleanup-old-sessions': {
            'task': 'tasks.analytics_jobs.cleanup_old_sessions',
            'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
        },
        'generate-daily-reports': {
            'task': 'tasks.report_generation.generate_daily_summary',
            'schedule': crontab(hour=0, minute=30),  # Daily at 12:30 AM
        },
        'update-analytics-cache': {
            'task': 'tasks.analytics_jobs.update_analytics_cache',
            'schedule': 300.0,  # Every 5 minutes
        },
        'health-check-cameras': {
            'task': 'tasks.video_processing.health_check_cameras',
            'schedule': 60.0,  # Every minute
        },
    },
)

if __name__ == '__main__':
    app.start()















