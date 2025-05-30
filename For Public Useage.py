
import streamlit as st
st.set_page_config(page_title="Grow a Garden Trade Tool", layout="wide")

import time
import sqlite3
from PIL import Image
import qrcode
from io import BytesIO
# ... any other imports

# === Constants ===
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

# === Utilities ===
def calculate_value(crop, weight, mutations):
    base_price = PRICE_PER_KG.get(crop, 0)
    total_multiplier = 1
    for mutation in mutations:
        total_multiplier *= MUTATION_MULTIPLIERS.get(mutation, 1)
    return weight * base_price * total_multiplier

def trade_fairness(value1, value2):
    if abs(value1 - value2) < 0.1 * max(value1, value2):
        return "Fair Trade"
    elif value1 > value2:
        return "Your Win"
    else:
        return "Your Loss"

def generate_qr_code(data):
    qr = qrcode.make(data)
    buf = BytesIO()
    qr.save(buf, format="PNG")
    return buf.getvalue()

# === Database Setup ===
conn = sqlite3.connect("/mount/data/growagarden.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS trades (code TEXT, user TEXT, offer TEXT)")
conn.commit()

# === Autorefresh every 3 seconds ===
st_autorefresh(interval=3000, limit=None, key="auto_refresh")

# === Session Setup ===
if "messages" not in st.session_state:
    st.session_state.messages = []

if "my_offer" not in st.session_state:
    st.session_state.my_offer = []

if "trade_code" not in st.session_state:
    st.session_state.trade_code = None

if "mode" not in st.session_state:
    st.session_state.mode = "calculator"  # calculator, trade-1p, trade-2p

# === Sidebar Mode Selector ===
st.sidebar.title("Modes")
st.session_state.mode = st.sidebar.selectbox("Select Mode", ["Calculator", "1-Person Trade", "2-Person Trade"])

# === Trade Code Logic ===
def save_offer(trade_code, user, offer_data):
    cursor.execute("REPLACE INTO trades (code, user, offer) VALUES (?, ?, ?)", (trade_code, user, offer_data))
    conn.commit()

def get_other_offer(trade_code, user):
    cursor.execute("SELECT user, offer FROM trades WHERE code=? AND user<>?", (trade_code, user))
    row = cursor.fetchone()
    return eval(row[1]) if row else []

# === Calculator Mode ===
if st.session_state.mode == "Calculator":
    st.title("Grow a Garden Crop Value Calculator")
    crop = st.selectbox("Select Crop", list(PRICE_PER_KG.keys()))
    weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1)
    mutations = st.multiselect("Mutations", list(MUTATION_MULTIPLIERS.keys()))

    if st.button("Calculate"):
        total_value = calculate_value(crop, weight, mutations)
        st.success(f"Total Value: ${total_value:,.2f}")

# === 1 or 2-Person Trade Mode ===
else:
    st.title("Grow a Garden Trade Center")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Your Offer")
        username = st.text_input("Enter Your Name", key="user1")
        st.session_state.my_offer = []
        for i in range(5):
            crop = st.selectbox(f"Crop {i+1}", list(PRICE_PER_KG.keys()), key=f"crop_{i}")
            weight = st.number_input(f"Weight {i+1}", min_value=0.0, step=0.1, key=f"weight_{i}")
            mutations = st.multiselect(f"Mutations {i+1}", list(MUTATION_MULTIPLIERS.keys()), key=f"mutations_{i}")
            st.session_state.my_offer.append((crop, weight, mutations))

        if st.button("Generate Trade Code") or not st.session_state.trade_code:
            st.session_state.trade_code = str(abs(hash(username + str(time.time()))))[:6]

        save_offer(st.session_state.trade_code, username, str(st.session_state.my_offer))
        st.info(f"Your Trade Code: `{st.session_state.trade_code}`")
        st.image(generate_qr_code(st.session_state.trade_code), width=150)

    with col2:
        st.subheader("Other Offer")
        if st.session_state.mode == "2-Person Trade":
            other_offer = get_other_offer(st.session_state.trade_code, username)
            if other_offer:
                for i, (crop, weight, mutations) in enumerate(other_offer):
                    st.markdown(f"**Crop {i+1}:** {crop}, {weight}kg")
                    st.markdown(f"- Mutations: {', '.join(mutations) if mutations else 'None'}")
            else:
                st.warning("Waiting for other person to join this trade...")
        else:
            st.markdown("This is a single-person trade. No comparison needed.")

    # Value comparison
    your_value = sum(calculate_value(c, w, m) for c, w, m in st.session_state.my_offer)
    other_value = sum(calculate_value(c, w, m) for c, w, m in get_other_offer(st.session_state.trade_code, username)) if st.session_state.mode == "2-Person Trade" else 0

    st.subheader("Trade Summary")
    st.write(f"Your Offer Value: ${your_value:,.2f}")
    if st.session_state.mode == "2-Person Trade":
        st.write(f"Other Offer Value: ${other_value:,.2f}")
        st.write(f"Trade Result: **{trade_fairness(your_value, other_value)}**")
