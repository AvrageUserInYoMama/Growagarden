import streamlit as st
import random
import sqlite3
import os
from datetime import datetime

# === DATABASE SETUP ===
DB_FILE = "trades.db"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                code TEXT PRIMARY KEY,
                username TEXT,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                code TEXT,
                sender TEXT,
                message TEXT,
                time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS offers (
                code TEXT,
                owner TEXT,
                crop TEXT,
                weight REAL,
                mutation TEXT,
                custom_price REAL
            )
        """)

init_db()

# === CROP AND MUTATION DATA ===
CROP_PRICES = {
    "Carrot": 30, "Strawberry": 90, "Blueberry": 40, "Orange Tulip": 750,
    "Tomato": 80, "Corn": 100, "Daffodil": 60, "Raspberry": 1500,
    "Pear": 2000, "Pineapple": 3000, "Peach": 100, "Apple": 375,
    "Grape": 10000, "Venus Fly Trap": 15000, "Mango": 6500,
    "Dragon Fruit": 4750, "Cursed Fruit": 50000, "Soul Fruit": 10500,
    "Candy Blossom": 100000, "Lotus": 20000, "Durian": 4500,
    "Bamboo": 1200, "Coconut": 2500, "Pumpkin": 1000, "Watermelon": 1200,
    "Cactus": 3000, "Passionfruit": 8000, "Pepper": 14000,
    "Starfruit": 7500, "Moonflower": 6000, "Moonglow": 9000,
    "Blood Banana": 1200, "Moon Melon": 15000, "Beanstalk": 18000,
    "Moon Mango": 36000,
}

MUTATION_MULTIPLIERS = {
    "None": 1.0, "Wet": 2, "Chilled": 2, "Chocolate": 2, "Moonlit": 2,
    "Bloodlit": 4, "Plasma": 5, "Frozen": 10, "Golden": 20,
    "Zombified": 25, "Shocked": 50, "Rainbow": 50, "Celestial": 120,
    "Disco": 125, "Twisted": 30
}

# === STREAMLIT SETUP ===
st.set_page_config("🌱 Grow a Garden  Calculator", layout="wide")

# === UTILITY FUNCTIONS ===
def calculate_value(crop, weight, mutation, use_weight, custom_price=None):
    base_price = custom_price if custom_price is not None else CROP_PRICES.get(crop, 0)
    multiplier = MUTATION_MULTIPLIERS.get(mutation, 1.0)
    return (weight if use_weight else 1) * base_price * multiplier

def summarize_trade(offers, use_weight):
    return sum(calculate_value(*offer, use_weight) for offer in offers)

def save_trade_to_db(code, owner, offers):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("DELETE FROM offers WHERE code=? AND owner=?", (code, owner))
        for crop, weight, mutation, price in offers:
            conn.execute("INSERT INTO offers VALUES (?, ?, ?, ?, ?, ?)", (code, owner, crop, weight, mutation, price))

def get_trade_offers(code, owner):
    with sqlite3.connect(DB_FILE) as conn:
        return conn.execute("SELECT crop, weight, mutation, custom_price FROM offers WHERE code=? AND owner=?", (code, owner)).fetchall()

def post_message(code, sender, msg):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("INSERT INTO messages VALUES (?, ?, ?, ?)", (code, sender, msg, datetime.now()))

def get_messages(code):
    with sqlite3.connect(DB_FILE) as conn:
        return conn.execute("SELECT sender, message, time FROM messages WHERE code=? ORDER BY time ASC", (code,)).fetchall()

# === UI ===
st.title("🌱 Grow a Garden  Calculator")

mode = st.radio("Choose Mode", ["Calculator Mode", "Trading Mode"], horizontal=True)

if mode == "Calculator Mode":
    use_custom = st.checkbox("Use Custom Item")
    crop = st.text_input("Item Name") if use_custom else st.selectbox("Select Crop", list(CROP_PRICES.keys()))
    custom_price = st.number_input("Custom Price", min_value=0.0) if use_custom else None
    use_weight = st.radio("Calculation Method", ["Base Price", "Weight-based"]) == "Weight-based"
    weight = st.number_input("Weight", min_value=0.1) if use_weight or use_custom else 1
    mutation = st.selectbox("Mutation", list(MUTATION_MULTIPLIERS.keys()))
    val = calculate_value(crop, weight, mutation, use_weight, custom_price)
    st.success(f"Value of {crop}: ₲{val:.2f}")

else:
    trade_mode = st.radio("Trade Mode", ["1 Person", "2 People"], horizontal=True)
    username = st.text_input("Your Username")
    if trade_mode == "2 People":
        if 'code' not in st.session_state:
            if st.button("Generate Trade Code"):
                code = str(random.randint(100000, 999999))
                with sqlite3.connect(DB_FILE) as conn:
                    conn.execute("INSERT OR IGNORE INTO trades (code, username) VALUES (?, ?)", (code, username))
                st.session_state.code = code

        join_code = st.text_input("Join Existing Code", placeholder="Enter code")
        if st.button("Join Code"):
            with sqlite3.connect(DB_FILE) as conn:
                result = conn.execute("SELECT username FROM trades WHERE code=?", (join_code,)).fetchone()
                if result:
                    st.session_state.code = join_code
                else:
                    st.error("Invalid code")

    code = st.session_state.get("code", f"local-{username}")
    st.markdown(f"### Trade Code: `{code}`")

    def get_offer_input(prefix):
        offers = []
        for i in range(3):
            cols = st.columns([2, 1, 2, 1])
            crop = cols[0].selectbox(f"{prefix} Crop {i+1}", list(CROP_PRICES.keys()), key=f"{prefix}_crop_{i}")
            weight = cols[1].number_input("Weight", min_value=0.0, step=0.1, key=f"{prefix}_wt_{i}")
            mut = cols[2].selectbox("Mutation", list(MUTATION_MULTIPLIERS.keys()), key=f"{prefix}_mut_{i}")
            price = cols[3].number_input("Custom Price", min_value=0.0, step=0.1, key=f"{prefix}_price_{i}")
            offers.append((crop, weight, mut, price if price > 0 else None))
        return offers

    your_offer = get_offer_input("you")
    if st.button("💾 Save Your Offer"):
        save_trade_to_db(code, "you", your_offer)
        st.success("Your offer has been saved.")

    if trade_mode == "2 People":
        their_offer = get_offer_input("them")
        if st.button("💾 Save Their Offer"):
            save_trade_to_db(code, "them", their_offer)
            st.success("Their offer has been saved.")
    else:
        their_offer = []

    use_weight = st.checkbox("Use weight-based values?", value=True)
    your_val = summarize_trade(your_offer, use_weight)
    their_val = summarize_trade(their_offer, use_weight)

    result = "Fair" if abs(your_val - their_val) < 0.1 else "Win" if your_val < their_val else "Loss"
    st.markdown(f"### ⚖️ Trade Result: **{result}**")
    st.write(f"Your Total: ₲{your_val:.2f}")
    st.write(f"Their Total: ₲{their_val:.2f}")

    st.subheader("💬 Messages")
    msg = st.text_input("Send message")
    if st.button("📨 Send"):
        if msg:
            post_message(code, username, msg)

    for sender, message, time in get_messages(code):
        st.write(f"🗨️ [{sender}]: {message} ({time.split('.')[0]})")
