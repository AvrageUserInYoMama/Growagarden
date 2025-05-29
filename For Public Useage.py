# Grow a Garden Trade Calculator (Improved UI & Logic)
import streamlit as st
import random

st.set_page_config(page_title="Grow a Garden Trade Calculator", layout="wide")

# === Crop Prices and Mutation Multipliers ===
CROP_PRICES = {
    "Carrot": 1.0,
    "Tomato": 2.0,
    "Potato": 1.5,
    "Pumpkin": 3.0
}

MUTATION_MULTIPLIERS = {
    "None": 1.0,
    "Silver": 1.2,
    "Gold": 1.5,
    "Rainbow": 2.0,
    "Diamond": 2.5,
    "Emerald": 3.0,
    "Galaxy": 4.0,
    "Mystic": 5.0
}

# === Session State Init ===
if "messages" not in st.session_state:
    st.session_state.messages = []
if "trades" not in st.session_state:
    st.session_state.trades = {}

# === Utility Functions ===
def calculate_value(crop, weight, mutation, use_weight, custom_price=None):
    base_price = custom_price if custom_price is not None else CROP_PRICES.get(crop, 0)
    mutation_multiplier = MUTATION_MULTIPLIERS.get(mutation, 1)
    return (weight if use_weight else 1) * base_price * mutation_multiplier

def summarize_trade(yours, theirs, use_weight):
    your_total = sum(calculate_value(crop, weight, mut, use_weight, price) for crop, weight, mut, price in yours)
    their_total = sum(calculate_value(crop, weight, mut, use_weight, price) for crop, weight, mut, price in theirs)
    return your_total, their_total

def fair_trade_result(your_value, their_value):
    if your_value == 0 and their_value == 0:
        return "Start building your trade."
    if your_value > their_value:
        return "This trade is a Loss"
    elif your_value < their_value:
        return "This trade is a Win"
    else:
        return "This trade is Fair"

# === Main Interface ===
st.title("🌱 Grow a Garden Trade Calculator")

# Trading vs Calculator mode
mode = st.radio("Choose Mode", ["Calculator Mode", "Trading Mode"], horizontal=True)

if mode == "Calculator Mode":
    st.header("🔢 Crop Calculator")
    use_custom = st.checkbox("Enable Custom Item")

    if use_custom:
        item_name = st.text_input("Custom Item Name")
        item_price = st.number_input("Set Custom Base Price", min_value=0.0, step=0.1)
    else:
        item_name = st.selectbox("Select Crop", list(CROP_PRICES.keys()))
        item_price = None

    use_weight = st.radio("Calculation Mode", ["Weight-based", "Base Price"], horizontal=True)
    is_weight = use_weight == "Weight-based"

    if use_custom or is_weight:
        weight = st.number_input("Enter Weight", min_value=0.0, step=0.1)
    else:
        weight = 1

    mutation = st.selectbox("Select Mutation", list(MUTATION_MULTIPLIERS.keys()))

    value = calculate_value(item_name, weight, mutation, is_weight, item_price)
    st.success(f"Value of {item_name} = ₲{value:.2f}")

elif mode == "Trading Mode":
    st.header("🤝 Trading Mode")
    st.markdown("Manage your trade and check fairness.")

    # Fairness Summary at top
    st.markdown("### ⚖️ Trade Fairness")

    with st.container():
        col1, col2 = st.columns([3, 3])

        with col1:
            st.subheader("Trade Setup")
            use_custom = st.checkbox("Enable Custom Items")
            if st.button("Generate Trade Code"):
                username = st.text_input("Enter your Roblox Username", key="gen_user")
                if username:
                    code = str(random.randint(100000, 999999999))
                    st.session_state.trades[code] = {"user": username, "your_offer": [], "their_offer": [], "messages": []}
                    st.success(f"Trade Code: {code}")

        with col2:
            st.subheader("Enter Trade Code to Join")
            join_code = st.text_input("", placeholder="Paste code here", key="join_code")
            if st.button("Join Trade"):
                if join_code in st.session_state.trades:
                    st.success("Joined trade!")
                else:
                    st.error("Invalid code")

    use_weight = st.radio("Calculation Method", ["Weight-based", "Base Price"], horizontal=True, key="weight_toggle")
    is_weight = use_weight == "Weight-based"

    st.divider()

    def trade_inputs(prefix):
        crops, weights, muts, prices = [], [], [], []
        for i in range(3):
            cols = st.columns([2, 1, 2, 1])
            crop = cols[0].selectbox(f"Crop {prefix}{i}", list(CROP_PRICES.keys()), key=f"crop_{prefix}{i}")
            weight = cols[1].number_input(f"Weight {prefix}{i}", min_value=0.0, step=0.1, key=f"wt_{prefix}{i}")
            mut = cols[2].selectbox("Mutation", list(MUTATION_MULTIPLIERS.keys()), key=f"mut_{prefix}{i}")
            if use_custom:
                custom_price = cols[3].number_input("Custom Price", min_value=0.0, step=0.1, key=f"price_{prefix}{i}")
            else:
                custom_price = None
            crops.append((crop, weight, mut, custom_price))
        return crops

    your_offer = trade_inputs("your")
    st.subheader("Their Offer")
    their_offer = trade_inputs("their")

    your_val, their_val = summarize_trade(your_offer, their_offer, is_weight)
    result = fair_trade_result(your_val, their_val)
    st.markdown(f"### ⚖️ {result}")

    st.subheader("Trade Summary")
    st.write(f"Your Offer Value: ₲{your_val:.2f}")
    st.write(f"Their Offer Value: ₲{their_val:.2f}")

    st.subheader("💬 Trade Messaging")
    new_msg = st.text_input("Send a message")
    if st.button("Send Message"):
        if new_msg:
            st.session_state.messages.append(new_msg)
    for msg in st.session_state.messages:
        st.write(f"🗨️ {msg}")
