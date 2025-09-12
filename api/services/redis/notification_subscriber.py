import asyncio
import json
import logging
import redis
from typing import Dict, Any
from api import config

logger = logging.getLogger(__name__)

class RedisNotificationSubscriber:
    """Redis subscriber for Celery task notifications"""
    
    def __init__(self):
        self.redis_client = None
        self.pubsub = None
        self.running = False
        
    def get_redis_client(self):
        """Get Redis client for pub/sub"""
        try:
            return redis.Redis(
                host=config.cache.REDIS_HOST,
                port=config.cache.REDIS_PORT,
                password=config.cache.REDIS_PASSWORD,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
        except Exception as e:
            logger.error(f"Failed to create Redis client: {e}")
            return None
    
    async def start_subscriber(self, websocket_emit_callback):
        """Start Redis subscriber and listen for notifications"""
        self.redis_client = self.get_redis_client()
        if not self.redis_client:
            logger.error("Failed to create Redis client for subscriber")
            return
            
        self.pubsub = self.redis_client.pubsub()
        self.pubsub.subscribe("celery_notifications")
        
        logger.info("🔔 Redis notification subscriber started")
        self.running = True
        
        try:
            # Get subscription confirmation first
            message = self.pubsub.get_message(timeout=1.0)
            if message and message['type'] == 'subscribe':
                logger.info(f"🔔 Subscribed to {message['channel']}")
            
            while self.running:
                try:
                    # Use asyncio.sleep to yield control and prevent blocking
                    await asyncio.sleep(0.1)
                    
                    message = self.pubsub.get_message(timeout=0.1)  # Short timeout
                    if message and message['type'] == 'message':
                        try:
                            notification = json.loads(message['data'])
                            logger.info(f"🔔 Received notification: {notification['type']}")
                            
                            # Call the WebSocket emit callback
                            await websocket_emit_callback(notification)
                            
                        except Exception as e:
                            logger.error(f"Error processing notification: {e}")
                            
                except Exception as e:
                    logger.error(f"Error in subscriber loop: {e}")
                    await asyncio.sleep(1)  # Wait before retrying
                        
        except Exception as e:
            logger.error(f"Redis subscriber error: {e}")
        finally:
            if self.pubsub:
                self.pubsub.close()
            logger.info("🔔 Redis notification subscriber stopped")
    
    def stop_subscriber(self):
        """Stop the Redis subscriber"""
        self.running = False
        if self.pubsub:
            self.pubsub.close()

# Global subscriber instance
notification_subscriber = RedisNotificationSubscriber()
