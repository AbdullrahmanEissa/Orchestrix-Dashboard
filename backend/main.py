from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any
import datetime

# Import database setup and models.
import models
from database import engine, get_db

# Create tables automatically at startup if they do not exist.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Server Orchestration Dashboard API")

# ==========================================
# 1. Pydantic Models (incoming payload schema)
# ==========================================
class SystemMetrics(BaseModel):
    cpu_percent: float
    memory_percent: float
    disk_percent: float

class AgentPayload(BaseModel):
    server_name: str
    system: SystemMetrics
    system_logs: List[str]
    containers: List[Dict[str, Any]]
    timestamp: float

# ==========================================
# 2. WebSocket Manager (real-time connection handling)
# ==========================================
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

# ==========================================
# 3. API Endpoints (core routes)
# ==========================================

@app.post("/api/metrics", tags=["Agent"])
async def receive_metrics(payload: AgentPayload, db: Session = Depends(get_db)):
    """
    Agent payload is received here, saved to the database,
    and broadcast live to the dashboard.
    """
    try:
        # --- Part 1: persist data in the database ---
        
        # 1. Find the server record, create it if missing.
        server = db.query(models.Server).filter(models.Server.name == payload.server_name).first()
        if not server:
            server = models.Server(name=payload.server_name)
            db.add(server)
            db.commit()
            db.refresh(server)

        # 2. Save resource metrics (CPU and RAM) as a new record.
        new_metric = models.Metric(
            cpu_percent=payload.system.cpu_percent,
            memory_percent=payload.system.memory_percent,
            server_id=server.id
        )
        db.add(new_metric)
        
        # 3. Update server last-seen timestamp.
        server.last_seen = datetime.datetime.utcnow()
        db.commit()

        # --- Part 2: real-time broadcast via WebSockets ---
        
        # Broadcast full payload so UI can render containers and logs live.
        await manager.broadcast({
            "event": "server_update",
            "server_name": payload.server_name,
            "payload": payload.dict()
        })
        
        return {"status": "success", "message": f"Data saved for {payload.server_name}"}
    
    except Exception as e:
        db.rollback() # Roll back transaction on any error.
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/servers", tags=["Dashboard"])
async def get_all_servers(db: Session = Depends(get_db)):
    """
    Dashboard endpoint to fetch all registered servers.
    """
    servers = db.query(models.Server).all()
    return {"total_servers": len(servers), "servers": servers}

# ==========================================
# 4. WebSocket Endpoint (live dashboard channel)
# ==========================================

@app.websocket("/ws/dashboard")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection open and wait for frontend messages.
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)