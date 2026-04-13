import streamlit as st # type: ignore

def render_kpi_row(total: int, positive_pct: float, negative_pct: float, active_topics: int):
    """Render the top-level metric cards uniformly."""
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.metric(
            label="Total Vol Evaluated", 
            value=f"{total:,}"
        )
    with c2:
        st.metric(
            label="Positive Index", 
            value=f"{positive_pct:.1f}%", 
            delta=f"{(positive_pct - 33.3):.1f}% vs avg", 
            delta_color="normal"
        )
    with c3:
        st.metric(
            label="Negative Index", 
            value=f"{negative_pct:.1f}%", 
            delta=f"{(negative_pct - 33.3):.1f}% vs avg", 
            delta_color="inverse"
        )
    with c4:
        st.metric(
            label="Active LDA Topics", 
            value=active_topics
        )
