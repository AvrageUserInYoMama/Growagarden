import streamlit as st
import random
import sqlite3
import time
from PIL import Image
import qrcode
from io import BytesIO

# === Constants ===
CROP_PRICES = {
    "Carrot": 30,
    "Strawberry": 90,
    "Blueberry": 40,
    "Orange Tulip": 750,
    "Tomato": 80,
    "Corn": 100,
    "Daffodil": 60,
    "Raspberry": 1500,
    "Pear": 2000,
    "Pineapple": 3000,
    "Peach": 100,
    "Apple": 375,
    "Grape": 10000,
    "Venus Fly Trap": 15000,
    "Mango": 6500,
    "Dragon Fruit": 4750,
    "Cursed Fruit": 50000,
    "Soul Fruit": 10500,
    "Candy Blossom": 100000,
    "Lotus": 20000,
    "Durian": 4500,
    "Bamboo": 1200,
    "Coconut": 2500,
    "Pumpkin": 1000,
    "Watermelon": 1200,
    "Cactus": 3000,
    "Passionfruit": 8000,
    "Pepper": 14000,
    "Starfruit": 7500,
    "Moonflower": 6000,
    "Moonglow": 9000,
    "Blood Banana": 1200,
    "Moon Melon": 15000,
    "Beanstalk": 18000,
    "Moon Mango": 36000,
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

# === DB Setup for persistence ===
conn = sqlite3.connect("trades.db", check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS trades (
    code TEXT PRIMARY KEY,
    username TEXT,
    your_offer TEXT,
    their_offer TEXT,
    messages TEXT,
    joined INTEGER DEFAULT 0
)''')
conn.commit()

# === Session State Initialization ===
if "trade_code" not in st.session_state:
    st.session_state.trade_code = ""
if "trade_data" not in st.session_state:
    st.session_state.trade_data = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "trade_mode" not in st.session_state:
    st.session_state.trade_mode = "1 Person"
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "trade_history" not in st.session_state:
    st.session_state.trade_history = []

# === Page config and theme ===
def set_theme(dark):
    if dark:
        st.markdown(
            """
            <style>
            .main {
                background-color: #0e1117;
                color: white;
            }
            </style>
            """, unsafe_allow_html=True)
    else:
        st.markdown(
            """
            <style>
            .main {
                background-color: white;
                color: black;
            }
            </style>
            """, unsafe_allow_html=True)

set_theme(st.session_state.dark_mode)
st.set_page_config(page_title="🌱 Grow a Garden Trade Calculator", layout="wide")

# === Utility Functions ===
import json

def serialize_offer(offer):
    # offer is list of tuples: (crop, weight, [mutations], custom_price)
    return json.dumps(offer)

def deserialize_offer(offer_str):
    return json.loads(offer_str) if offer_str else []

def serialize_messages(msgs):
    return json.dumps(msgs)

def deserialize_messages(msgs_str):
    return json.loads(msgs_str) if msgs_str else []

def calculate_value(crop, weight, mutations, use_weight, custom_price=None):
    base_price = custom_price if custom_price is not None else CROP_PRICES.get(crop, 0)
    # multiply all mutation multipliers together
    mutation_multiplier = 1
    for mut in mutations:
        mutation_multiplier *= MUTATION_MULTIPLIERS.get(mut, 1)
    # Use price per kg if weight mode is enabled
    price_per_unit = PRICE_PER_KG.get(crop, base_price)
    if use_weight:
        return weight * price_per_unit * mutation_multiplier
    else:
        return base_price * mutation_multiplier

def summarize_trade(yours, theirs, use_weight):
    your_total = sum(calculate_value(crop, weight, muts, use_weight, price) for crop, weight, muts, price in yours)
    their_total = sum(calculate_value(crop, weight, muts, use_weight, price) for crop, weight, muts, price in theirs)
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

def generate_trade_code():
    while True:
        code = str(random.randint(100000, 999999))
        c.execute("SELECT code FROM trades WHERE code=?", (code,))
        if not c.fetchone():
            return code

def save_trade_to_db(code, username, your_offer, their_offer, messages, joined):
    c.execute('''INSERT OR REPLACE INTO trades
                 (code, username, your_offer, their_offer, messages, joined)
                 VALUES (?, ?, ?, ?, ?, ?)''',
                 (code, username,
                  serialize_offer(your_offer),
                  serialize_offer(their_offer),
                  serialize_messages(messages),
                  joined))
    conn.commit()

def load_trade_from_db(code):
    c.execute("SELECT * FROM trades WHERE code=?", (code,))
    row = c.fetchone()
    if row:
        return {
            "code": row[0],
            "username": row[1],
            "your_offer": deserialize_offer(row[2]),
            "their_offer": deserialize_offer(row[3]),
            "messages": deserialize_messages(row[4]),
            "joined": bool(row[5])
        }
    return None

def update_trade_messages(code, new_messages):
    trade = load_trade_from_db(code)
    if trade:
        messages = trade["messages"]
        messages.extend(new_messages)
        save_trade_to_db(code, trade["username"], trade["your_offer"], trade["their_offer"], messages, trade["joined"])

# === UI Helpers ===
def draw_qr_code(code):
    qr = qrcode.make(code)
    buf = BytesIO()
    qr.save(buf)
    buf.seek(0)
    img = Image.open(buf)
    st.image(img, caption="Trade Code QR", width=150)

def trade_input_row(prefix, idx, use_custom):
    cols = st.columns([3, 2, 3, 2])
    crop = cols[0].selectbox(f"Crop {prefix}{idx}", list(CROP_PRICES.keys()), key=f"crop_{prefix}{idx}")
    weight = cols[1].number_input(f"Weight {prefix}{idx}", min_value=0.0, step=0.1, key=f"wt_{prefix}{idx}")
    mut_str = cols[2].text_input("Mutations (comma separated)", key=f"mut_{prefix}{idx}", help="E.g. Wet,Golden")
    mutations = [m.strip() for m in mut_str.split(",") if m.strip()]
    custom_price = None
    if use_custom:
        custom_price = cols[3].number_input(f"Custom Price {prefix}{idx}", min_value=0.0, step=1.0, key=f"custom_{prefix}{idx}")
    else:
        cols[3].write("N/A")
    return crop, weight, mutations, custom_price

# === Main UI ===
st.title("🌱 Grow a Garden Trade Calculator")

# Dark mode toggle
dark_toggle = st.sidebar.checkbox("Dark Mode", value=st.session_state.dark_mode)
if dark_toggle != st.session_state.dark_mode:
    st.session_state.dark_mode = dark_toggle
    set_theme(dark_toggle)
    st.experimental_rerun()

# Trade mode selection
st.sidebar.markdown("### Trade Mode")
trade_mode = st.sidebar.radio("Select number of people:", ["1 Person", "2 People"], index=0 if st.session_state.trade_mode=="1 Person" else 1)
st.session_state.trade_mode = trade_mode

# Username input
username = st.sidebar.text_input("Enter your Roblox Username", key="username")

# Use weight mode or not
use_weight = st.sidebar.checkbox("Use Weight-Based Pricing", value=True)

# Use custom items
use_custom = st.sidebar.checkbox("Enable Custom Prices", value=False)

# Generate or join trade code
if st.session_state.trade_code == "":
    if st.button("Create New Trade Code"):
        st.session_state.trade_code = generate_trade_code()
        st.session_state.trade_data = {
            "your_offer": [],
            "their_offer": [],
            "messages": [],
            "joined": False,
            "username": username
        }
        save_trade_to_db(st.session_state.trade_code, username, [], [], [], 0)
else:
    st.markdown(f"**Trade Code:** `{st.session_state.trade_code}`")
    draw_qr_code(st.session_state.trade_code)
    if not st.session_state.trade_data:
        st.session_state.trade_data = load_trade_from_db(st.session_state.trade_code)

join_code_input = st.text_input("Join Trade by Code")
if join_code_input and join_code_input != st.session_state.trade_code:
    trade_loaded = load_trade_from_db(join_code_input)
    if trade_loaded:
        st.session_state.trade_code = join_code_input
        st.session_state.trade_data = trade_loaded
        # Mark joined true if joining other's trade
        if not trade_loaded["joined"]:
            trade_loaded["joined"] = True
            save_trade_to_db(join_code_input, trade_loaded["username"], trade_loaded["your_offer"], trade_loaded["their_offer"], trade_loaded["messages"], 1)
    else:
        st.error("Invalid trade code!")

# Input offers
st.subheader("Your Offer")
your_offer = []
num_offers = 3  # Could be dynamic if you want to add/remove rows
for i in range(num_offers):
    crop, weight, mutations, custom_price = trade_input_row("your_", i+1, use_custom)
    your_offer.append((crop, weight, mutations, custom_price))

if st.session_state.trade_mode == "2 People":
    st.subheader("Their Offer (Read-Only)")
    their_offer = st.session_state.trade_data["their_offer"] if st.session_state.trade_data else []
    for i, (crop, weight, mutations, custom_price) in enumerate(their_offer):
        st.markdown(f"**Crop {i+1}:** {crop} | Weight: {weight} | Mutations: {', '.join(mutations)} | Price: {custom_price if custom_price else CROP_PRICES.get(crop, 'N/A')}")

else:
    their_offer = []

# Save your offer button
if st.button("Save Your Offer"):
    if st.session_state.trade_code:
        # Save your offer to DB
        save_trade_to_db(st.session_state.trade_code, username, your_offer, their_offer, st.session_state.messages, int(st.session_state.trade_data["joined"] if st.session_state.trade_data else 0))
        st.success("Offer saved!")
        # Update session state trade data for immediate UI update
        st.session_state.trade_data = load_trade_from_db(st.session_state.trade_code)

# Calculate trade values and result
your_value, their_value = summarize_trade(your_offer, their_offer, use_weight)
result = fair_trade_result(your_value, their_value)

st.markdown(f"### Trade Summary")
st.markdown(f"- Your Offer Value: {your_value:.2f}")
st.markdown(f"- Their Offer Value: {their_value:.2f}")
st.markdown(f"**Result: {result}**")

# === Messaging ===
st.subheader("Trade Chat")

if "chat_input" not in st.session_state:
    st.session_state.chat_input = ""

def append_message(sender, text):
    st.session_state.messages.append({"sender": sender, "text": text, "timestamp": time.time()})
    if st.session_state.trade_code:
        save_trade_to_db(st.session_state.trade_code, username, your_offer, their_offer, st.session_state.messages, int(st.session_state.trade_data["joined"] if st.session_state.trade_data else 0))

chat_col1, chat_col2 = st.columns([4,1])
with chat_col1:
    chat_text = st.text_input("Enter message", key="chat_input")
with chat_col2:
    if st.button("Send"):
        if chat_text.strip() != "":
            append_message(username, chat_text.strip())
            st.session_state.chat_input = ""

# Display messages with timestamps
for msg in st.session_state.messages[-50:]:
    sender = msg["sender"]
    text = msg["text"]
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(msg["timestamp"]))
    st.markdown(f"**{sender}** [{timestamp}]: {text}")

# Auto-refresh chat every 3 seconds
st.experimental_set_query_params(_=int(time.time()))  # trick to refresh page periodically
st_autorefresh = st.experimental_memo(lambda: time.sleep(3))  # keep memo to prevent tight loop

# === Trade History ===
st.sidebar.markdown("### Trade History (This session)")
if len(st.session_state.trade_history) > 0:
    for code in st.session_state.trade_history:
        st.sidebar.markdown(f"- `{code}`")
else:
    st.sidebar.markdown("No trades yet.")

if st.session_state.trade_code and st.session_state.trade_code not in st.session_state.trade_history:
    st.session_state.trade_history.append(st.session_state.trade_code)

# === End ===
