import streamlit as st
import pandas as pd
import numpy as np
from polygon import RESTClient
from datetime import datetime
import plotly.graph_objects as go

st.set_page_config(page_title="GrokGamma", layout="wide", page_icon="🚀")
st.title("🚀 GrokGamma — Institutional Spot Gamma Dashboard")
st.caption("Real-time GEX • Call Wall • Put Wall • Gamma Flip • Dealer Positioning | Powered by Grok + Polygon.io")

# ====================== SIDEBAR ======================
st.sidebar.header("⚙️ Controls")

# API Key
if "polygon" in st.secrets:
    api_key = st.secrets["polygon"]["api_key"]
    st.sidebar.success("✅ API key loaded securely")
else:
    api_key = st.sidebar.text_input("Polygon API Key", type="password", 
                                    help="Get free key at polygon.io → paste here")

underlying = st.sidebar.text_input("Ticker (SPX, SPY, AAPL, etc.)", value="SPX")
max_dte = st.sidebar.slider("Max Days to Expiration", 1, 90, 45)
refresh_btn = st.sidebar.button("🔄 Refresh Live Data", type="primary", use_container_width=True)

# ====================== CORE TOOL ======================
@st.cache_data(ttl=300)
def fetch_gammas(underlying: str, max_dte: int, api_key: str):
    client = RESTClient(api_key)
    snapshots = list(client.list_snapshot_options_chain(underlying))
    
    data = []
    spot = snapshots[0].underlying_asset.price if snapshots else None
    today = datetime.now().date()
    
    for s in snapshots:
        if not s.greeks or not s.greeks.gamma or s.open_interest == 0:
            continue
        try:
            exp_date = datetime.strptime(s.details.expiration_date, "%Y-%m-%d").date()
            dte = (exp_date - today).days
            if dte < 0 or dte > max_dte:
                continue
        except:
            continue
            
        gex = s.greeks.gamma * s.open_interest * 100 * (spot ** 2) * 0.01
        sign = 1 if s.details.contract_type == "call" else -1
        data.append({
            "strike": s.details.strike_price,
            "dte": dte,
            "type": s.details.contract_type,
            "gamma": s.greeks.gamma,
            "oi": s.open_interest,
            "gex": sign * gex,
            "spot": spot
        })
    
    df = pd.DataFrame(data)
    return df, spot

def compute_profile(df):
    if df.empty:
        return None, None, None, None, None
    profile = df.groupby("strike")["gex"].sum().reset_index().sort_values("strike")
    net_gex = profile["gex"].sum()
    
    call_wall = profile.loc[profile["gex"].idxmax(), "strike"]
    put_wall = profile.loc[profile["gex"].idxmin(), "strike"]
    flip_idx = (profile["gex"] * profile["gex"].shift(1) < 0).idxmax()
    gamma_flip = profile.loc[flip_idx, "strike"] if flip_idx != 0 else None
    
    return profile, net_gex, call_wall, put_wall, gamma_flip

# ====================== RUN ======================
if refresh_btn or st.session_state.get("first_run", True):
    st.session_state.first_run = False
    if not api_key:
        st.error("Please enter your Polygon API key in the sidebar")
        st.stop()
    
    with st.spinner(f"Fetching {underlying} options chain... (10–30s for SPX)"):
        df, spot = fetch_gammas(underlying, max_dte, api_key)
    
    if df.empty:
        st.error("No data returned. Try SPY instead of SPX or check your API key.")
        st.stop()
    
    profile, net_gex, call_wall, put_wall, gamma_flip = compute_profile(df)
    
    # ====================== HEADER METRICS ======================
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Spot Price", f"${spot:,.2f}")
    regime = "🟢 LONG GAMMA (low vol, pinning expected)" if net_gex > 0 else "🔴 SHORT GAMMA (high vol, breakouts likely)"
    col2.metric("Net GEX", f"${net_gex:,.0f}", delta=regime)
    col3.metric("Call Wall", f"{call_wall:,}")
    col4.metric("Put Wall", f"{put_wall:,}")
    
    st.markdown(f"**Gamma Flip:** {gamma_flip:,}" if gamma_flip else "**Gamma Flip:** Not detected")
    
    # ====================== CHART ======================
    st.subheader("Gamma Exposure Profile")
    fig = go.Figure()
    colors = ["#00ff88" if g > 0 else "#ff4444" for g in profile["gex"]]
    fig.add_trace(go.Bar(x=profile["strike"], y=profile["gex"], name="GEX", marker_color=colors, width=8))
    fig.add_vline(x=spot, line_dash="dash", line_color="#4488ff", annotation_text=f"Spot ${spot:,.0f}", annotation_position="top")
    fig.update_layout(height=580, template="plotly_dark", xaxis_title="Strike Price", yaxis_title="Gamma Exposure ($ per 1% move)")
    st.plotly_chart(fig, use_container_width=True)
    
    # ====================== TABLE ======================
    st.subheader("Key Levels & Top GEX Strikes")
    display_profile = profile.copy()
    display_profile["gex"] = display_profile["gex"].map("${:,.0f}".format)
    st.dataframe(display_profile.nlargest(15, "gex").reset_index(drop=True), use_container_width=True)
    
    st.caption("Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

else:
    st.info("👈 Click **Refresh Live Data** in the sidebar to load the chart")
