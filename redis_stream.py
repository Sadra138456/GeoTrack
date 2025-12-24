import redis.asyncio as redis
import json, asyncio, os
from websocket_manager import manager


REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
PUB_SUB_CHANNEL = "location_updates"


r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

async def redis_listener():
    """Background task to listen for Redis messages and forward to WebSockets."""
    pubsub = r.pubsub()
    await pubsub.subscribe(PUB_SUB_CHANNEL)
    print(f"Redis Listener started on channel: {PUB_SUB_CHANNEL}")
    
    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                data = json.loads(message['data']) 
                device_id = data.get("device_id")
                # send into the seperated manager
                await manager.send_personal_message(device_id, data)
            await asyncio.sleep(0.01)
    except Exception as e:           
        print(f"Redis Listener Error: {e}")
        
        
        
async def publish_update(data: dict):
     """Utility to publish data to Redis Pub/Sub"""
     await r.publish(PUB_SUB_CHANNEL, json.dumps(data))