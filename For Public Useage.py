import streamlit as st
import random

if "trades" not in st.session_state:
    st.session_state.trades = {}

st.title("Trade Code Test")

trading_mode = st.checkbox("Enable Trading Mode")

if trading_mode:
    st.header("Share Your Offer")

    if st.button("Generate Trade ID"):
        trade_id = str(random.randint(10000000, 99999999))
        st.session_state.trades[trade_id] = {"message": ""}
        st.session_state.generated_trade_id = trade_id

    if "generated_trade_id" in st.session_state:
        st.write(f"🆔 Your Trade ID: `{st.session_state.generated_trade_id}`")
        msg = st.text_input("Optional Message", key="msg_out")
        st.session_state.trades[st.session_state.generated_trade_id]["message"] = msg
        st.success("Copy this Trade ID and share it with the other person!")

    st.header("Load a Trade")
    load_id = st.text_input("Enter Trade ID")
    if load_id in st.session_state.trades:
        offer = st.session_state.trades[load_id]
        st.write(f"Message from trade owner: {offer['message']}")

else:
    st.write("Trading mode is OFF")
