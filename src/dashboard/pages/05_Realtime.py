import streamlit as st # type: ignore
import json
import logging
import asyncio
import pandas as pd
from websockets.client import connect # type: ignore
from src.dashboard.config import COLOR_MAP, WS_BASE_URL
import plotly.express as px

logger = logging.getLogger(__name__)

st.title("⚡ Real-time Stream")
st.markdown("Live WebSocket feed from collectors and NLP pipeline.")

# Reconnection configuration
WS_URL = WS_BASE_URL
MAX_MSGS = 20

# Persist stream data in session state
if "stream_data" not in st.session_state:
    st.session_state.stream_data = []

async def ws_consumer():
    """Consumes websocket messages with automatic exponential backoff reconnection."""
    retry_delay = 1
    placeholder = st.empty()
    
    while True:
        try:
            async with connect(WS_URL) as websocket:
                retry_delay = 1 # Reset on success
                st.sidebar.success("✅ Connected to Stream")
                
                # Send optional subscription if needed
                await websocket.send(json.dumps({"type": "subscribe", "keywords": []}))
                
                while True:
                    message_raw = await websocket.recv()
                    msg = json.loads(message_raw)
                    
                    if msg.get("type") == "ping":
                        await websocket.send(json.dumps({"type": "pong"}))
                        continue
                        
                    # Prepend new message
                    st.session_state.stream_data.insert(0, msg)
                    if len(st.session_state.stream_data) > MAX_MSGS:
                        st.session_state.stream_data.pop()
                    
                    # Force UI update
                    with placeholder.container():
                        render_stream_ui()
                        
        except Exception as e:
            st.sidebar.error(f"❌ Connection lost: {e}")
            logger.warning(f"WS Disconnect: {e}. Retrying in {retry_delay}s...")
            await asyncio.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 60) # Backoff to max 60s

def render_stream_ui():
    """Renders the actual live cards."""
    if not st.session_state.stream_data:
        st.info("Waiting for incoming messages...")
        return
        
    for item in st.session_state.stream_data:
        label = item.get("sentiment", {}).get("label", "neutral")
        color = COLOR_MAP.get(label.capitalize(), "#888888")
        
        with st.container():
            st.markdown(f"""
            <div style='border-left: 5px solid {color}; padding: 10px; margin: 5px 0; background: #262730; border-radius: 5px;'>
                <small style='color: #aaa;'>{item.get('platform', 'unknown')} | {item.get('user', 'anonymous')}</small><br>
                <b>{item.get('text', 'No text')}</b><br>
                <span style='color: {color}; font-weight: bold;'>{label.upper()}</span> | 
                <small>Confidence: {item.get('sentiment', {}).get('confidence', 0):.1%}</small>
            </div>
            """, unsafe_allow_html=True)

# Run the async loop inside Streamlit
if st.button("Start Live Stream") or "stream_running" in st.session_state:
    st.session_state.stream_running = True
    try:
        asyncio.run(ws_consumer())
    except Exception as e:
        st.error(f"Stream encountered a critical failure: {e}")
        del st.session_state["stream_running"]
