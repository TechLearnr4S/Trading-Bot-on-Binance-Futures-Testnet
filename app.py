import logging
import os
import sys

import streamlit as st
from dotenv import load_dotenv

from bot.client import BinanceClient
from bot.orders import place_limit_order, place_market_order, place_stop_limit_order

# ---------------------------------------------------------
# Page Configuration (Must be the first Streamlit command)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Testnet Trading Bot",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------
# Backend Initialization
# ---------------------------------------------------------
@st.cache_resource
def get_client():
    load_dotenv()
    api_key = os.getenv("BINANCE_API_KEY", "").strip()
    api_secret = os.getenv("BINANCE_API_SECRET", "").strip()
    
    if not api_key or not api_secret:
        return None
    return BinanceClient(api_key=api_key, api_secret=api_secret)

client = get_client()

# ---------------------------------------------------------
# UI Layout (Fully Responsive)
# ---------------------------------------------------------
st.title("📈 Binance Testnet Bot")
st.markdown("Easily place orders on the USDT-M Futures Testnet.")

if not client:
    st.error(
        "**Missing API Credentials!**\n\n"
        "Please ensure `BINANCE_API_KEY` and `BINANCE_API_SECRET` are set in your `.env` file."
    )
    st.stop()

with st.container():
    # Top Row: Symbol
    symbol = st.selectbox(
        "Trading Pair (Symbol)",
        options=["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT"],
        index=0
    )

    # Middle Row: Side, Type, Quantity
    # Streamlit columns automatically stack on mobile devices!
    col1, col2, col3 = st.columns(3)
    
    with col1:
        side = st.selectbox("Order Side", ["BUY", "SELL"])
        # Give it a color hint based on side
        color = "green" if side == "BUY" else "red"
        st.markdown(f"<h3 style='text-align: center; color: {color}; margin-top:-10px;'>{side}</h3>", unsafe_allow_html=True)
        
    with col2:
        order_type = st.selectbox("Order Type", ["MARKET", "LIMIT", "STOP"])
        
    with col3:
        quantity = st.number_input("Quantity", value=0.01, step=0.01, min_value=0.001)

    # Conditional inputs based on order type
    price = None
    stop_price = None

    if order_type in ["LIMIT", "STOP"]:
        price = st.number_input("Limit Price (USDT)", value=50000.0, step=100.0)
        
    if order_type == "STOP":
        stop_price = st.number_input("Stop/Trigger Price (USDT)", value=50000.0, step=100.0)

    st.markdown("---")
    
    # Action Button
    # Streamlit handles button sizing natively for touch targets
    if st.button("🚀 Execute Order", type="primary", use_container_width=True):
        if not symbol:
            st.warning("Please enter a valid symbol.")
            st.stop()
            
        with st.spinner(f"Placing {order_type} {side} order for {symbol}..."):
            try:
                if order_type == "MARKET":
                    response = place_market_order(client, symbol, side, quantity)
                elif order_type == "LIMIT":
                    response = place_limit_order(client, symbol, side, quantity, price)
                elif order_type == "STOP":
                    response = place_stop_limit_order(client, symbol, side, quantity, price, stop_price)
                
                st.success("✅ Order placed successfully!")
                
                # Show key details in a clean responsive expander rather than dumping JSON
                with st.expander("View Order Details", expanded=True):
                    st.write(f"**Order ID:** `{response.get('orderId')}`")
                    st.write(f"**Status:** `{response.get('status')}`")
                    st.write(f"**Executed Qty:** `{response.get('executedQty')}`")
                    st.json(response)
                    
            except Exception as e:
                st.error(f"❌ Failed to place order: {e}")
