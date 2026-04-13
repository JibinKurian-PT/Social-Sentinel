import json
import asyncio
from fastapi import WebSocket, WebSocketDisconnect # type: ignore
from src.api.websocket.manager import manager
import logging

logger = logging.getLogger(__name__)

async def handle_websocket_messages(websocket: WebSocket):
    """Event handler loop for a single websocket connection with keepalive handling."""
    try:
        while True:
            # We wait for messages but use a timeout so we don't hold the loop forever if totally stuck
            try:
                # 60 second read timeout
                data = await asyncio.wait_for(websocket.receive_text(), timeout=65.0)
            except asyncio.TimeoutError:
                # If we haven't received a pong or message in 65s, let's assume dead
                logger.warning("WebSocket dead: missed keepalive/timeout")
                break
                
            try:
                payload = json.loads(data)
                msg_type = payload.get("type")
                
                if msg_type == "subscribe":
                    keywords = payload.get("keywords", [])
                    await manager.subscribe(websocket, keywords)
                    await manager.send_personal_message(
                        json.dumps({"type": "subscribed", "keywords": keywords}), websocket
                    )
                    
                elif msg_type == "ping":
                    # Respond with pong for client-initiated pings
                    await manager.send_personal_message(json.dumps({"type": "pong"}), websocket)
                    
                elif msg_type == "pong":
                    # Heartbeat acknowledgment from client, nothing to do, just resets the read timeout
                    pass
                    
            except json.JSONDecodeError:
                await manager.send_personal_message(
                    json.dumps({"error": "Invalid JSON format"}), websocket
                )
                
    except WebSocketDisconnect:
        # Expected exit path
        pass
    except Exception as e:
        logger.error(f"WebSocket closed by server error or client abrupt disconnect: {e}")
    finally:
        manager.disconnect(websocket)
