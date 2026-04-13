import streamlit as st # type: ignore
import pandas as pd # type: ignore
import folium # type: ignore
from streamlit_folium import st_folium # type: ignore
from src.dashboard.config import API_BASE_URL, COLOR_MAP, API_KEY
from src.dashboard.utils import get_from_api, handle_api_error
import logging

logger = logging.getLogger(__name__)

st.title("🗺️ Geographic Sentiment Map")
st.markdown("Visualizing brand perception across global locations.")

@st.cache_data(ttl=120)
def fetch_geo_data():
    try:
        # Note: Geo router now returns actual DB locations + lat/lon via geopy
        data = get_from_api(f"{API_BASE_URL}/geo", headers={"X-API-Key": API_KEY})
        return data
    except Exception as e:
        handle_api_error(e, "fetching geographic data")
        return []

try:
    geo_data = fetch_geo_data()
    
    if not geo_data:
        st.warning("Insufficient location data to generate map. Ensure posts have 'location' tags.")
    else:
        # Init Folium Map centered on Atlantic
        m = folium.Map(location=[20, 0], zoom_start=2, tiles="CartoDB dark_matter")
        
        for p in geo_data:
            lat = p.get("latitude")
            lon = p.get("longitude")
            if lat is None or lon is None: continue
            
            color = COLOR_MAP.get(p["dominant_sentiment"].capitalize(), "gray")
            
            folium.CircleMarker(
                location=[lat, lon],
                radius=min(30, max(5, p["count"] / 100)), # bubble size by volume
                popup=f"<b>{p['location']}</b><br>Sentiment: {p['dominant_sentiment']}<br>Vol: {p['count']}",
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.7
            ).add_to(m)
            
        st_folium(m, width=1100, height=600)
        
        # Bottom Data Table
        st.subheader("Regional Stats Breakdown")
        df_geo = pd.DataFrame(geo_data).drop(columns=["latitude", "longitude"], errors="ignore")
        st.dataframe(df_geo, use_container_width=True)

except Exception as e:
    st.error("Map layer failed to initialize.")
    logger.exception("GeoMap page crash")
