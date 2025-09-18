#!/usr/bin/env python3
"""
Test script for S3 completion notifications with user-specific rooms
"""
import redis
import json
import time
from api import config

def test_s3_notification():
    """Test S3 completion notification"""
    print("🔔 Testing S3 completion notification...")
    
    # Connect to Redis
    r = redis.Redis(
        host=config.cache.REDIS_HOST,
        port=config.cache.REDIS_PORT,
        password=config.cache.REDIS_PASSWORD,
        decode_responses=True
    )
    
    # Test S3 completion notification
    test_notification = {
        'type': 's3_upload_complete',
        'job_id': '123',
        'user_id': '456',
        's3_url': 'https://tenx-parrot-assets.s3.amazonaws.com/audio/test.mp3',
        'bucket': 'tenx-parrot-assets',
        'key': 'audio/test.mp3',
        'filename': 'test.mp3',
        'content_type': 'audio/mpeg',
        'timestamp': time.time()
    }
    
    print(f"📤 Publishing S3 completion notification: {test_notification}")
    r.publish('celery_notifications', json.dumps(test_notification))
    
    print("✅ S3 notification test completed")
    print("📡 Check WebSocket logs for room: processing_123_456")

if __name__ == "__main__":
    test_s3_notification()




