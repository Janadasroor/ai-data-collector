import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="AI Data Collector Dashboard")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

def load_stats() -> Dict:
    """Load statistics from file"""
    stats_file = Path("crawler_stats.json")
    if stats_file.exists():
        with open(stats_file, 'r') as f:
            return json.load(f)
    return {
        "pages_crawled": 0,
        "code_files_collected": 0,
        "total_mb": 0,
        "pages_failed": 0,
        "duplicates_skipped": 0,
        "elapsed_hours": 0,
        "pages_per_minute": 0
    }

def load_checkpoint() -> Dict:
    """Load checkpoint state"""
    checkpoint_file = Path("crawler_state.json")
    if checkpoint_file.exists():
        with open(checkpoint_file, 'r') as f:
            return json.load(f)
    return {
        "visited_urls": [],
        "urls_to_visit": [],
        "statistics": {}
    }

def get_recent_data(limit: int = 10) -> List[Dict]:
    """Get recent collected data"""
    data_file = Path("training_data.jsonl")
    if not data_file.exists():
        return []
    
    recent = []
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines[-limit:]:
                try:
                    recent.append(json.loads(line))
                except:
                    pass
    except:
        pass
    
    return list(reversed(recent))

def count_total_items() -> int:
    """Count total items in data file"""
    data_file = Path("training_data.jsonl")
    if not data_file.exists():
        return 0
    
    try:
        with open(data_file, 'r') as f:
            return sum(1 for _ in f)
    except:
        return 0

@app.get("/")
async def get_dashboard():
    """Serve the dashboard HTML"""
    return FileResponse("static/index.html")

@app.get("/api/stats")
async def get_stats():
    """Get current statistics"""
    stats = load_stats()
    checkpoint = load_checkpoint()
    
    return {
        "stats": stats,
        "queue_size": len(checkpoint.get("urls_to_visit", [])),
        "visited_count": len(checkpoint.get("visited_urls", [])),
        "total_items": count_total_items(),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/recent-data")
async def get_recent():
    """Get recently collected data"""
    return {
        "data": get_recent_data(20),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/config")
async def get_config():
    """Get current configuration"""
    config_file = Path("config.json")
    if config_file.exists():
        with open(config_file, 'r') as f:
            return json.load(f)
    return {}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        # Send initial data
        stats = load_stats()
        checkpoint = load_checkpoint()
        await websocket.send_json({
            "type": "stats",
            "data": {
                "stats": stats,
                "queue_size": len(checkpoint.get("urls_to_visit", [])),
                "visited_count": len(checkpoint.get("visited_urls", [])),
                "total_items": count_total_items()
            }
        })
        
        # Keep connection alive and send updates
        while True:
            # Wait for messages or send periodic updates
            try:
                # Send stats every 2 seconds
                await asyncio.sleep(2)
                stats = load_stats()
                checkpoint = load_checkpoint()
                await websocket.send_json({
                    "type": "stats",
                    "data": {
                        "stats": stats,
                        "queue_size": len(checkpoint.get("urls_to_visit", [])),
                        "visited_count": len(checkpoint.get("visited_urls", [])),
                        "total_items": count_total_items()
                    }
                })
            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"WebSocket error: {e}")
                break
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

@app.get("/api/logs")
async def get_logs():
    """Get recent log entries"""
    log_file = Path("crawler.log")
    if not log_file.exists():
        return {"logs": []}
    
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
            recent_logs = lines[-50:]  # Last 50 lines
            return {"logs": [line.strip() for line in recent_logs]}
    except:
        return {"logs": []}

if __name__ == "__main__":
    print("🚀 Starting AI Data Collector Dashboard...")
    print("📊 Dashboard URL: http://localhost:8000")
    print("🔌 WebSocket URL: ws://localhost:8000/ws")
    print("\nPress Ctrl+C to stop")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
