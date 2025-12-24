from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Any

class ConnectionManager:
    """
    Manages active WebSocket connections by storing them in memory.
    Note: This local in-memory storage is not scalable and will be fixed in Phase 4 
    using Redis Pub/Sub.
    """
    def __init__(self):
        # Stores active connections in the format: {device_id: WebSocket}
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, device_id: str, websocket: WebSocket):
        """Registers and accepts a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[device_id] = websocket
        print(f"🔗 WebSocket connected for device: {device_id}")

    def disconnect(self, device_id: str):
        """Removes a disconnected connection."""
        if device_id in self.active_connections:
            del self.active_connections[device_id]
            print(f"❌ WebSocket disconnected for device: {device_id}")

    async def send_personal_message(self, device_id: str, message: Dict[str, Any]):
        """Sends a JSON message to a specific device via its WebSocket."""
        if device_id in self.active_connections:
            try:
                await self.active_connections[device_id].send_json(message)
                return True
            except Exception as e:
                # Cleanup if sending fails (e.g., client suddenly closes connection)
                print(f"Error sending to {device_id}: {e}")
                self.disconnect(device_id) 
                return False
        return False

# Global instance of the ConnectionManager
manager = ConnectionManager()