import streamlit as st # type: ignore

def render_sidebar_filters():
    """Render standard filters that sync across all pages via st.session_state."""
    st.sidebar.markdown("### Global Filters")
    
    # Time window
    if "filter_time" not in st.session_state:
        st.session_state.filter_time = "Last 24 Hours"
        
    time_opts = ["Last 1 Hour", "Last 24 Hours", "Last 7 Days", "Last 30 Days"]
    st.session_state.filter_time = st.sidebar.selectbox("Time Window", time_opts, index=time_opts.index(st.session_state.filter_time))
    
    # Platforms
    if "filter_platforms" not in st.session_state:
        st.session_state.filter_platforms = ["twitter", "youtube"]
        
    platforms = ["twitter", "youtube", "reddit"]
    st.session_state.filter_platforms = st.sidebar.multiselect("Platforms", platforms, default=st.session_state.filter_platforms)
    
    # Sentiment
    if "filter_sentiment" not in st.session_state:
        st.session_state.filter_sentiment = ["Positive", "Neutral", "Negative"]
        
    st.session_state.filter_sentiment = st.sidebar.multiselect("Sentiment", ["Positive", "Neutral", "Negative"], default=st.session_state.filter_sentiment)
    
    # Keyword search
    if "filter_search" not in st.session_state:
        st.session_state.filter_search = ""
        
    st.session_state.filter_search = st.sidebar.text_input("Contains Keyword", value=st.session_state.filter_search)
