import streamlit as st
import random
from datetime import datetime

# --- Data (same as before) ---
CROP_PRICES = {
    # ... same crop price dictionary ...
    "Carrot": 30,
    "Strawberry": 90,
    # (you can paste all your prices here)
}
PRICE_PER_KG = {
    # ... same price per kg dictionary ...
    "Carrot": 100,
    "Strawberry": 80,
    # (you can paste all your prices here)
}
MUTATION_MULTIPLIERS = {
    "Wet": 2,
    "Chilled": 2,
    "Chocolate": 2,
    "Moonlit": 2,
    "Bloodlit": 4,
    "Plasma": 5,
    "Frozen": 10,
    "Golden": 20,
    "Zombified": 25,
    "Shocked": 50,
    "Rainbow": 50,
    "Celestial": 120,
    "Disco": 125,
    "Twisted": 30,
}

STACKABLE_MUTATIONS = {
    frozenset(["Wet", "Chilled"]): "Frozen",
}

# --- Helper functions (same) ---
def calculate_value(crop, weight, base_price, mutations, method):
    mutations_to_apply = set(mutations)
    for combo, result in STACKABLE_MUTATIONS.items():
        if combo.issubset(mutations_to_apply):
            mutations_to_apply.difference_update(combo)
            mutations_to_apply.add(result)
    base = base_price if method == "Base Price" else PRICE_PER_KG.get(crop, 0) * weight
    final_multiplier = sum(MUTATION_MULTIPLIERS.get(m, 0) for m in mutations_to_apply)
    return base * (1 + final_multiplier)

def trade_value_from_inputs(offers):
    total = 0.0
    for offer in offers:
        if offer["use_custom"]:
            base = offer["custom_price"]
        else:
            if offer["method"] == "Base Price":
                base = CROP_PRICES.get(offer["crop"], 0)
            else:
                base = PRICE_PER_KG.get(offer["crop"], 0) * offer["weight"]
        final_multiplier = sum(MUTATION_MULTIPLIERS.get(m, 0) for m in offer["mutations"])
        total += base * (1 + final_multiplier)
    return total

# --- Streamlit app start ---

st.title("Grow a Garden Crop Value Calculator with Trading Mode and Chat")

if "trades" not in st.session_state:
    st.session_state.trades = {}

trading_mode = st.checkbox("Enable Trading Mode")

if not trading_mode:
    st.write("Trading Mode is off. Use this mode to calculate crop value.")
    # Put your normal calculator here if you want
else:
    st.header("Trading Mode")

    # Your Offer input (simplified for demo)
    your_offers = []
    for i in range(2):  # smaller for demo
        st.markdown(f"### Your Offer Item {i+1}")
        use_custom = st.checkbox(f"Use custom price for item {i+1}?", key=f"your_custom_{i}")
        if use_custom:
            custom_name = st.text_input(f"Custom Item Name {i+1}", key=f"your_custom_name_{i}")
            custom_price = st.number_input(f"Custom Price {i+1}", min_value=0.0, format="%.2f", key=f"your_custom_price_{i}")
            weight = 0.0
            mutations = []
            crop_name = custom_name if custom_name else "Custom Item"
            method = "Base Price"
        else:
            crop_name = st.selectbox(f"Select Crop {i+1}", list(CROP_PRICES.keys()), key=f"your_crop_{i}")
            weight = st.number_input(f"Weight (kg) {i+1}", min_value=0.0, format="%.2f", key=f"your_weight_{i}")
            base_price_input = st.number_input(f"Or Base Price (0 to ignore) {i+1}", min_value=0.0, format="%.2f", value=0.0, key=f"your_base_price_{i}")
            mutations = st.multiselect(f"Select Mutations {i+1}", list(MUTATION_MULTIPLIERS.keys()), key=f"your_mutations_{i}")
            method = "Base Price" if base_price_input > 0 else "Weight-based"
            custom_price = 0.0

        your_offers.append({
            "crop": crop_name,
            "weight": weight,
            "base_price": base_price_input if not use_custom else custom_price,
            "mutations": mutations,
            "method": method,
            "use_custom": use_custom,
            "custom_price": custom_price,
        })

    # Their Offer input (same simplified)
    their_offers = []
    for i in range(2):
        st.markdown(f"### Their Offer Item {i+1}")
        use_custom = st.checkbox(f"Use custom price for their item {i+1}?", key=f"their_custom_{i}")
        if use_custom:
            custom_name = st.text_input(f"Their Custom Item Name {i+1}", key=f"their_custom_name_{i}")
            custom_price = st.number_input(f"Their Custom Price {i+1}", min_value=0.0, format="%.2f", key=f"their_custom_price_{i}")
            weight = 0.0
            mutations = []
            crop_name = custom_name if custom_name else "Custom Item"
            method = "Base Price"
        else:
            crop_name = st.selectbox(f"Their Crop {i+1}", list(CROP_PRICES.keys()), key=f"their_crop_{i}")
            weight = st.number_input(f"Their Weight (kg) {i+1}", min_value=0.0, format="%.2f", key=f"their_weight_{i}")
            base_price_input = st.number_input(f"Their Base Price (0 to ignore) {i+1}", min_value=0.0, format="%.2f", value=0.0, key=f"their_base_price_{i}")
            mutations = st.multiselect(f"Their Mutations {i+1}", list(MUTATION_MULTIPLIERS.keys()), key=f"their_mutations_{i}")
            method = "Base Price" if base_price_input > 0 else "Weight-based"
            custom_price = 0.0

        their_offers.append({
            "crop": crop_name,
            "weight": weight,
            "base_price": base_price_input if not use_custom else custom_price,
            "mutations": mutations,
            "method": method,
            "use_custom": use_custom,
            "custom_price": custom_price,
        })

    your_total = trade_value_from_inputs(your_offers)
    their_total = trade_value_from_inputs(their_offers)

    st.subheader(f"Your Offer Total Value: ₵{your_total:,.2f}")
    st.subheader(f"Their Offer Total Value: ₵{their_total:,.2f}")

    # Trade ID & message system
    st.header("Share Your Offer")

    if st.button("Generate Trade ID"):
        trade_id = str(random.randint(10000000, 99999999))
        # Initialize trade data with chat history
        st.session_state.trades[trade_id] = {
            "your_offers": your_offers,
            "your_total": your_total,
            "their_offers": their_offers,
            "their_total": their_total,
            "chat": [],  # list of messages: dict with sender, text, time
        }
        st.session_state.generated_trade_id = trade_id

    if "generated_trade_id" in st.session_state:
        st.write(f"🆔 Your Trade ID: `{st.session_state.generated_trade_id}`")
        st.success("Share this Trade ID with your trading partner to chat.")

    st.header("Load Trade & Chat")

    load_id = st.text_input("Enter Trade ID to load trade and chat")

    if load_id in st.session_state.trades:
        trade = st.session_state.trades[load_id]
        st.subheader(f"Loaded Trade ID: {load_id}")
        st.write(f"Your Offer Total: ₵{trade['your_total']:,.2f}")
        st.write(f"Their Offer Total: ₵{trade['their_total']:,.2f}")

        # Show chat messages
        st.markdown("### Chat")
        for msg in trade["chat"]:
            time_str = msg["time"].strftime("%H:%M:%S")
            if msg["sender"] == "You":
                st.markdown(f"**You [{time_str}]:** {msg['text']}")
            else:
                st.markdown(f"**Them [{time_str}]:** {msg['text']}")

        # Input new message
        new_msg = st.text_input("Type your message here", key=f"chat_input_{load_id}")
        sender_choice = st.radio("Send as:", options=["You", "Them"], horizontal=True, index=0, key=f"sender_radio_{load_id}")

        if st.button("Send Message", key=f"send_msg_btn_{load_id}"):
            if new_msg.strip():
                trade["chat"].append({
                    "sender": sender_choice,
                    "text": new_msg.strip(),
                    "time": datetime.now(),
                })
                st.experimental_rerun()  # refresh to show message immediately
            else:
                st.warning("Please type a message before sending.")

    elif load_id:
        st.warning("Trade ID not found.")

st.markdown("---")
st.markdown("🔹 Not affiliated with the Garden game developers.")
st.markdown("🔹 Prices are rough estimates.")
st.markdown("🔹 Made by Gregothey.")
