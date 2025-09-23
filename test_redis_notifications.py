#!/usr/bin/env python3
"""
Test script for Redis pub/sub notifications
"""
import redis
import json
import time
import asyncio
from api import config
from api.services.celery.socket_test_tasks import socket_test_task

def test_redis_pubsub():
    """Test Redis pub/sub functionality"""
    print("🔔 Testing Redis pub/sub notifications...")
    
    # Connect to Redis
    r = redis.Redis(
        host=config.cache.REDIS_HOST,
        port=config.cache.REDIS_PORT,
        password=config.cache.REDIS_PASSWORD,
        decode_responses=True
    )
    
    # Test notification
    test_notification = {
        'type': 'test_notification',
        'task_id': 'test-123',
        'job_profile_id': 123,
        'filename': 'test.wav',
        'timestamp': time.time()
    }
    
    print(f"📤 Publishing test notification: {test_notification}")
    r.publish('celery_notifications', json.dumps(test_notification))
    
    # Subscribe and listen
    pubsub = r.pubsub()
    pubsub.subscribe('celery_notifications')
    print("👂 Listening for notifications...")
    
    # Listen for a few seconds
    start_time = time.time()
    while time.time() - start_time < 5:
        message = pubsub.get_message(timeout=1.0)
        if message and message['type'] == 'message':
            notification = json.loads(message['data'])
            print(f"📥 Received notification: {notification}")
            break
        print(".", end="", flush=True)
    
    pubsub.close()
    print("\n✅ Redis pub/sub test completed")

if __name__ == "__main__":
    test_redis_pubsub()
    # Also enqueue the socket test event to room processing_123
    try:
        res = socket_test_task.delay(room="processing_123", message="hello from test script")
        print(f"📨 Enqueued socket_test_task: {res.id}")
    except Exception as e:
        print(f"❌ Failed to enqueue socket_test_task: {e}")
