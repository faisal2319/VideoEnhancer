#!/usr/bin/env python3
"""
Celery worker for the ML service
"""
import os
import sys

# Add the parent directory to the path so we can import from shared
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.celery_app import celery_app

if __name__ == '__main__':
    celery_app.start() 