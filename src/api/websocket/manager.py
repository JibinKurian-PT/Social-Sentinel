import asyncio
import json
from fastapi import WebSocket # type: ignore
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages active websocket client connections for realtime feeds."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.subscriptions: Dict[WebSocket, List[str]] = {}
        # Start heartbeat loop in background
        self._heartbeat_task = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.subscriptions[websocket] = []
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")
        
        # Ensure heartbeat task is running
        if self._heartbeat_task is None or self._heartbeat_task.done():
            self._heartbeat_task = asyncio.create_task(self.heartbeat_loop())

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.subscriptions:
            del self.subscriptions[websocket]
        logger.info(f"WebSocket disconnected. Total left: {len(self.active_connections)}")

    async def subscribe(self, websocket: WebSocket, keywords: List[str]):
        """Subscribe a connection to specific keywords."""
        if websocket in self.subscriptions:
            self.subscriptions[websocket].extend(keywords)
            self.subscriptions[websocket] = list(set(self.subscriptions[websocket]))

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception:
            self.disconnect(websocket)

    async def broadcast(self, message: dict):
        """Broadcasts only to subscribed websockets (or all if empty subscription)."""
        if not self.active_connections:
            return
            
        msg_text = json.dumps(message)
        dead_connections = []
        
        for connection in self.active_connections:
            try:
                # Filter by subscription if we have topics in the message
                subs = self.subscriptions.get(connection, [])
                if subs and "topic" in message:
                    if message["topic"].lower() not in [s.lower() for s in subs]:
                        continue
                
                await connection.send_text(msg_text)
            except Exception:
                dead_connections.append(connection)
                
        for dc in dead_connections:
            self.disconnect(dc)

    async def heartbeat_loop(self):
        """Background loop to send ping frames to prevent connection timeouts/drops."""
        while True:
            if not self.active_connections:
                break # Stop loop if no connections; it gets restarted on next connect
                
            await asyncio.sleep(30) # 30s heartbeat interval
            dead_connections = []
            
            for connection in self.active_connections:
                try:
                    # Some JS clients respond to native pings, but we send a custom 'ping' message just to be safe
                    await connection.send_text(json.dumps({"type": "ping", "heartbeat": True}))
                except Exception:
                    dead_connections.append(connection)
            
            for dc in dead_connections:
                self.disconnect(dc)

manager = ConnectionManager()
