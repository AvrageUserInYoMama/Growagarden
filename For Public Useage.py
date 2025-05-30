import streamlit as st
import sqlite3
import time
from PIL import Image
import qrcode
from io import BytesIO
import threading

# === Constants ===

BASE_PRICES = {
    "Carrot": 100,
    "Strawberry": 80,
    "Blueberry": 120,
    "Orange Tulip": 17000,
    "Tomato": 60,
    "Corn": 76,
    "Daffodil": 60,
    "Raspberry": 60,
    "Pear": 77,
    "Pineapple": 750,
    "Peach": 90,
    "Apple": 77.57,
    "Grape": 3300,
    "Venus Fly Trap": 1324,
    "Mango": 510,
    "Dragon Fruit": 70,
    "Cursed Fruit": 100,
    "Soul Fruit": 77,
    "Candy Blossom": 3900,
    "Lotus": 435,
    "Durian": 660,
    "Bamboo": 1051,
    "Coconut": 50,
    "Pumpkin": 60,
    "Watermelon": 80,
    "Cactus": 1110,
    "Passionfruit": 1400,
    "Pepper": 1850,
    "Starfruit": 5611,
    "Moonflower": 4000,
    "Moonglow": 3400,
    "Blood Banana": 4600,
    "Moon Melon": 130,
    "Beanstalk": 2344,
    "Moon Mango": 2277,
}

PRICE_PER_KG = {
    "Carrot": 100,
    "Strawberry": 80,
    "Blueberry": 120,
    "Orange Tulip": 17000,
    "Tomato": 60,
    "Corn": 76,
    "Daffodil": 60,
    "Raspberry": 60,
    "Pear": 77,
    "Pineapple": 750,
    "Peach": 90,
    "Apple": 77.57,
    "Grape": 3300,
    "Venus Fly Trap": 1324,
    "Mango": 510,
    "Dragon Fruit": 70,
    "Cursed Fruit": 100,
    "Soul Fruit": 77,
    "Candy Blossom": 3900,
    "Lotus": 435,
    "Durian": 660,
    "Bamboo": 1051,
    "Coconut": 50,
    "Pumpkin": 60,
    "Watermelon": 80,
    "Cactus": 1110,
    "Passionfruit": 1400,
    "Pepper": 1850,
    "Starfruit": 5611,
    "Moonflower": 4000,
    "Moonglow": 3400,
    "Blood Banana": 4600,
    "Moon Melon": 130,
    "Beanstalk": 2344,
    "Moon Mango": 2277,
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

# === DB SETUP ===
conn = sqlite3.connect("trades.db", check_same_thread=False)
c = conn.cursor()
c.execute(
    """
    CREATE TABLE IF NOT EXISTS trades (
        trade_code TEXT PRIMARY KEY,
        data TEXT,
        messages TEXT
    )
"""
)
conn.commit()

# === UTILITIES ===

def calculate_crop_value(crop, amount, mutations):
    base_price = BASE_PRICES.get(crop, 0)
    per_kg_price = PRICE_PER_KG.get(crop, 0)
    multiplier = 1
    for m in mutations:
        multiplier *= MUTATION_MULTIPLIERS.get(m, 1)
    # Base + (amount * price_per_kg) all times multiplier
    return (base_price + amount * per_kg_price) * multiplier

def calculate_offer_value(offer):
    total = 0
    for crop, details in offer.items():
        amount = details.get("amount", 0)
        mutations = details.get("mutations", [])
        total += calculate_crop_value(crop, amount, mutations)
    return total

def evaluate_trade(offer1, offer2):
    val1 = calculate_offer_value(offer1)
    val2 = calculate_offer_value(offer2)
    diff = val1 - val2
    if abs(diff) < 1e-5:
        return "Fair trade"
    elif diff > 0:
        return "You win"
    else:
        return "You lose"

def save_trade_to_db(trade_code, data, messages):
    c.execute(
        "INSERT OR REPLACE INTO trades (trade_code, data, messages) VALUES (?, ?, ?)",
        (trade_code, data, messages),
    )
    conn.commit()

def load_trade_from_db(trade_code):
    c.execute("SELECT data, messages FROM trades WHERE trade_code=?", (trade_code,))
    row = c.fetchone()
    if row:
        return row[0], row[1]
    return None, None

def generate_trade_code():
    import random
    import string

    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def generate_qr_code(text):
    qr = qrcode.QRCode(box_size=2)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    bio = BytesIO()
    img.save(bio, format="PNG")
    bio.seek(0)
    return bio

# === STREAMLIT PAGE SETUP ===
st.set_page_config(
    page_title="Grow a Garden Trade Calculator & Chat",
    layout="wide",
)

# === SESSION STATE SETUP ===
if "trade_code" not in st.session_state:
    st.session_state.trade_code = None
if "trade_data" not in st.session_state:
    st.session_state.trade_data = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "mode" not in st.session_state:
    st.session_state.mode = "1 Person"  # default mode

# === PAGE UI ===

st.title("🌱 Grow a Garden Trade Calculator & Chat")

mode = st.radio("Choose Trading Mode:", options=["1 Person", "2 People"], index=0)
st.session_state.mode = mode

# Generate or enter trade code section
if mode == "1 Person":
    if not st.session_state.trade_code:
        if st.button("Generate New Trade Code"):
            st.session_state.trade_code = generate_trade_code()
            st.session_state.trade_data = {}
            st.session_state.messages = []
            # Save initial empty trade
            save_trade_to_db(st.session_state.trade_code, "{}", "")
    st.markdown(f"**Your Trade Code:** `{st.session_state.trade_code}`")
else:
    trade_code_input = st.text_input("Enter Trade Code to Join")
    if trade_code_input:
        st.session_state.trade_code = trade_code_input.strip().upper()
        # Load trade data from DB
        data_json, messages_json = load_trade_from_db(st.session_state.trade_code)
        if data_json:
            import json
            try:
                st.session_state.trade_data = json.loads(data_json)
            except Exception:
                st.session_state.trade_data = {}
            try:
                st.session_state.messages = json.loads(messages_json) if messages_json else []
            except Exception:
                st.session_state.messages = []
        else:
            st.error("Invalid trade code or no such trade exists.")
            st.session_state.trade_data = None
            st.session_state.messages = []

# --- Trade Offer Setup ---

st.subheader("Your Trade Offer")

if st.session_state.trade_data is None:
    st.stop()

import json

if "your_offer" not in st.session_state:
    st.session_state.your_offer = {}

def offer_editor(label_prefix, offer_dict):
    # Let user add/edit crops and multiple mutations
    crops = list(BASE_PRICES.keys())
    new_offer = {}
    for i in range(10):  # limit to 10 crops max per offer for UI simplicity
        crop = st.selectbox(f"{label_prefix} Crop {i+1}", [""] + crops, key=f"{label_prefix}_crop_{i}")
        if not crop:
            continue
        amount = st.number_input(f"{label_prefix} Amount of {crop}", min_value=0, step=1, key=f"{label_prefix}_amount_{i}")
        mutations_str = st.text_input(f"{label_prefix} Mutations (comma separated)", key=f"{label_prefix}_mutations_{i}")
        mutations = [m.strip() for m in mutations_str.split(",") if m.strip()]
        new_offer[crop] = {"amount": amount, "mutations": mutations}
    return new_offer

st.session_state.your_offer = offer_editor("Your", st.session_state.your_offer)

# Save your offer back into trade data for mode 1 or mode 2 accordingly

if st.session_state.mode == "1 Person":
    st.session_state.trade_data = {"your_offer": st.session_state.your_offer}
    save_trade_to_db(st.session_state.trade_code, json.dumps(st.session_state.trade_data), json.dumps(st.session_state.messages))
elif st.session_state.mode == "2 People":
    if "your_offer" not in st.session_state.trade_data:
        st.session_state.trade_data["your_offer"] = {}
    if "their_offer" not in st.session_state.trade_data:
        st.session_state.trade_data["their_offer"] = {}

    # Let user choose if they are Player 1 or Player 2 for demo purposes
    player_role = st.radio("You are:", ["Player 1 (Your Offer)", "Player 2 (Their Offer)"])
    if player_role == "Player 1 (Your Offer)":
        st.session_state.trade_data["your_offer"] = st.session_state.your_offer
    else:
        # Player 2 edits "their_offer"
        their_offer = offer_editor("Their", st.session_state.trade_data.get("their_offer", {}))
        st.session_state.trade_data["their_offer"] = their_offer

    save_trade_to_db(st.session_state.trade_code, json.dumps(st.session_state.trade_data), json.dumps(st.session_state.messages))

# --- Display Both Offers for comparison ---

st.subheader("Trade Offers")

your_offer = st.session_state.trade_data.get("your_offer", {})
their_offer = st.session_state.trade_data.get("their_offer", {})

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Your Offer:**")
    if your_offer:
        for crop, details in your_offer.items():
            st.markdown(f"- {crop}: {details.get('amount',0)} units")
            if details.get("mutations"):
                st.markdown(f"  - Mutations: {', '.join(details['mutations'])}")
    else:
        st.write("No crops offered.")

with col2:
    st.markdown("**Their Offer:**")
    if their_offer:
        for crop, details in their_offer.items():
            st.markdown(f"- {crop}: {details.get('amount',0)} units")
            if details.get("mutations"):
                st.markdown(f"  - Mutations: {', '.join(details['mutations'])}")
    else:
        st.write("No crops offered.")

# --- Calculate and show fairness result ---

result_text = evaluate_trade(your_offer, their_offer)
st.markdown(f"### Trade Result: **{result_text}**")

# --- Chat Section with Autorefresh ---

st.subheader("Trade Chat")

if "chat_input" not in st.session_state:
    st.session_state.chat_input = ""

chat_col1, chat_col2 = st.columns([4, 1])

with chat_col1:
    chat_box = st.empty()

with chat_col2:
    msg = st.text_input("Type message", key="chat_input")
    send_clicked = st.button("Send")

if send_clicked and msg.strip():
    # Append new message with timestamp
    timestamp = time.strftime("%H:%M:%S")
    username = "You"  # For demo; could be replaced by username input
    st.session_state.messages.append(f"[{timestamp}] {username}: {msg.strip()}")
    # Save messages back to DB
    messages_json = json.dumps(st.session_state.messages)
    data_json = json.dumps(st.session_state.trade_data)
    save_trade_to_db(st.session_state.trade_code, data_json, messages_json)
    st.session_state.chat_input = ""

# Load chat messages continuously
def update_chat():
    data_json, messages_json = load_trade_from_db(st.session_state.trade_code)
    if messages_json:
        try:
            loaded_msgs = json.loads(messages_json)
            if loaded_msgs != st.session_state.messages:
                st.session_state.messages = loaded_msgs
        except Exception:
            pass

update_chat()

chat_box.text_area("Chat", value="\n".join(st.session_state.messages), height=250, key="chat_area", disabled=True)

# --- QR Code for Trade Code ---

if st.session_state.trade_code:
    qr_image = generate_qr_code(st.session_state.trade_code)
    st.markdown("### Share this QR Code for quick joining:")
    st.image(qr_image)

# --- Page refresh every 3 seconds to update chat and offers ---

def auto_refresh():
    time.sleep(3)
    st.experimental_rerun()

if st.session_state.trade_code:
    threading.Thread(target=auto_refresh, daemon=True).start()

# --- End of script ---
