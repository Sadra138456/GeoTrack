from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
import json, time, asyncio
from typing import Dict, Any

# custom modules
from websocket_manager import manager
from redis_stream import r, redis_listener, publish_update

app = FastAPI(title="GeoTrack API")

GEO_KEY = "device_locations"

@app.post("/update_location/{device_id}")
async def update_location(device_id: str, latitude: float, longitude: float):
    """Update device position, save to geo-index and notify via pub/sub"""
    now = time.time()
    
    try:
        # store coordinates in redis geo
        await r.geoadd(GEO_KEY, (longitude, latitude, device_id))
        
        # create update payload
        data = {
            "device_id": device_id,
            "type": "location_update",
            "lat": latitude,
            "lon": longitude,
            "timestamp": now
        }
        
        # cache last known position
        await r.set(f"device_meta:{device_id}", json.dumps(data))

        # broadcast to all server instances via redis pub/sub
        await publish_update(data)
        
        return {"status": "success", "device_id": device_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/nearby")
async def get_nearby(center_lat: float, center_lon: float, radius_km: float = 1.0):
    """Find devices within a specific radius"""
    nearby = await r.geosearch(
        GEO_KEY,
        longitude=center_lon, 
        latitude=center_lat,  
        radius=radius_km,     
        unit='km',            
        withcoord=True,
        sort='ASC'
    )

    results = []
    for item in nearby:
        dev_id, coords = item[0], item[1]
        
        # fetch extra meta if exists
        meta_raw = await r.get(f"device_meta:{dev_id}")
        meta = json.loads(meta_raw) if meta_raw else {}

        results.append({
            "device_id": dev_id,
            "lat": coords[1],
            "lon": coords[0],
            "metadata": meta
        })
        
    return {"nearby_devices": results}


@app.websocket("/ws/tracker/{device_id}")
async def websocket_endpoint(websocket: WebSocket, device_id: str):
    """Handle live websocket connections per device"""
    await manager.connect(device_id, websocket)
    try:
        while True:
            # keep connection alive
            await websocket.receive_text()
    except (WebSocketDisconnect, RuntimeError):
        manager.disconnect(device_id)


@app.on_event("startup")
async def startup_event():
    # run redis pub/sub listener in background
    asyncio.create_task(redis_listener())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)