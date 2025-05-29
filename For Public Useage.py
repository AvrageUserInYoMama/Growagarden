import streamlit as st
import random
import time
import sqlite3
from contextlib import closing

st.set_page_config(page_title="Grow a Garden Trade Calculator", layout="wide")

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

# For the Single User mode default mutations list with "None"
SINGLE_USER_MUTATIONS = ["None"] + list(MUTATION_MULTIPLIERS.keys())

# === SQLite DB Setup for Multi User mode ===

DB_PATH = "growagarden_trades.db"

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with closing(get_db()) as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS trades (
            code TEXT PRIMARY KEY,
            username TEXT,
            created_at INTEGER
        );
        CREATE TABLE IF NOT EXISTS offers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trade_code TEXT,
            owner TEXT,
            crop TEXT,
            weight REAL,
            mutation TEXT,
            custom_price REAL,
            FOREIGN KEY(trade_code) REFERENCES trades(code)
        );
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trade_code TEXT,
            username TEXT,
            message TEXT,
            timestamp INTEGER,
            FOREIGN KEY(trade_code) REFERENCES trades(code)
        );
        """)
        db.commit()

init_db()

# === Utility Functions ===

def calculate_value(crop, weight, mutation, use_weight, custom_price=None):
    base_price = custom_price if custom_price is not None else CROP_PRICES.get(crop, 0)
    mutation_multiplier = MUTATION_MULTIPLIERS.get(mutation, 1)
    val = (weight if use_weight else 1) * base_price * mutation_multiplier
    return val

def summarize_trade(offers, use_weight):
    total = 0
    for offer in offers:
        total += calculate_value(
            offer["crop"],
            offer["weight"],
            offer["mutation"],
            use_weight,
            offer["custom_price"],
        )
    return total

def fair_trade_result(your_value, their_value):
    if your_value == 0 and their_value == 0:
        return "Start building your trade."
    if your_value > their_value:
        return "This trade is a Loss"
    elif your_value < their_value:
        return "This trade is a Win"
    else:
        return "This trade is Fair"

# --- Multi User DB functions ---

def create_trade(username):
    code = str(random.randint(100000, 999999999))
    now = int(time.time())
    with closing(get_db()) as db:
        db.execute("INSERT INTO trades (code, username, created_at) VALUES (?, ?, ?)", (code, username, now))
        db.commit()
    return code

def get_trade(code):
    with closing(get_db()) as db:
        trade = db.execute("SELECT * FROM trades WHERE code=?", (code,)).fetchone()
    return trade

def get_offers(code, owner):
    with closing(get_db()) as db:
        rows = db.execute("SELECT * FROM offers WHERE trade_code=? AND owner=?", (code, owner)).fetchall()
        return [dict(row) for row in rows]

def save_offers(code, owner, offers):
    with closing(get_db()) as db:
        # Delete old offers
        db.execute("DELETE FROM offers WHERE trade_code=? AND owner=?", (code, owner))
        # Insert new offers
        for offer in offers:
            db.execute(
                "INSERT INTO offers (trade_code, owner, crop, weight, mutation, custom_price) VALUES (?, ?, ?, ?, ?, ?)",
                (code, owner, offer["crop"], offer["weight"], offer["mutation"], offer["custom_price"])
            )
        db.commit()

def get_messages(code):
    with closing(get_db()) as db:
        rows = db.execute("SELECT * FROM messages WHERE trade_code=? ORDER BY timestamp ASC", (code,)).fetchall()
        return [dict(row) for row in rows]

def insert_message(code, username, message):
    now = int(time.time())
    with closing(get_db()) as db:
        db.execute(
            "INSERT INTO messages (trade_code, username, message, timestamp) VALUES (?, ?, ?, ?)",
            (code, username, message, now)
        )
        db.commit()

# === Streamlit Interface ===

st.title("🌱 Grow a Garden Trade Calculator")

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

    mutation = st.selectbox("Select Mutation", SINGLE_USER_MUTATIONS if use_custom else list(MUTATION_MULTIPLIERS.keys()))

    value = calculate_value(item_name, weight, mutation, is_weight, item_price)
    st.success(f"Value of {item_name} = ₲{value:.2f}")

elif mode == "Trading Mode":
    st.header("🤝 Trading Mode")

    trade_type = st.radio("Trade Type", ["Single User", "Multi User"])

    if trade_type == "Single User":
        # --- Single User Mode (session_state) ---
        if "messages" not in st.session_state:
            st.session_state.messages = []

        if "trade_offers" not in st.session_state:
            default_offer = {
                "crop": "Carrot",
                "weight": 0.0,
                "mutation": "None",
                "custom_price": None,
            }
            st.session_state.trade_offers = {
                "your": [default_offer.copy() for _ in range(3)],
                "their": [default_offer.copy() for _ in range(3)],
            }

        username = st.text_input("Enter your Roblox Username (for chat)", key="username_single")

        def input_offers(owner):
            st.subheader(f"{owner.capitalize()}'s Offer")
            offers = st.session_state.trade_offers[owner]
            use_custom = st.checkbox("Enable Custom Prices", key=f"custom_prices_{owner}")
            use_weight = st.radio("Calculation Mode", ["Weight-based", "Base Price"], key=f"use_weight_{owner}", horizontal=True)
            is_weight = use_weight == "Weight-based"

            for i in range(3):
                cols = st.columns([3, 2, 3, 2])
                offers[i]["crop"] = cols[0].selectbox(f"Crop {owner} {i+1}", list(CROP_PRICES.keys()), index=list(CROP_PRICES.keys()).index(offers[i]["crop"]), key=f"crop_{owner}_{i}")
                offers[i]["weight"] = cols[1].number_input(f"Weight {owner} {i+1}", min_value=0.0, step=0.1, value=offers[i]["weight"], key=f"weight_{owner}_{i}")
                mut_list = SINGLE_USER_MUTATIONS if st.session_state.get(f"custom_prices_{owner}", False) else list(MUTATION_MULTIPLIERS.keys())
                offers[i]["mutation"] = cols[2].selectbox(f"Mutation {owner} {i+1}", mut_list, index=mut_list.index(offers[i]["mutation"]) if offers[i]["mutation"] in mut_list else 0, key=f"mutation_{owner}_{i}")
                if use_custom:
                    cp_val = offers[i]["custom_price"] if offers[i]["custom_price"] is not None else 0.0
                    offers[i]["custom_price"] = cols[3].number_input(f"Custom Price {owner} {i+1}", min_value=0.0, step=0.1, value=cp_val, key=f"custom_price_{owner}_{i}")
                else:
                    offers[i]["custom_price"] = None
            st.session_state.trade_offers[owner] = offers
            return offers, is_weight

        your_offers, your_weight_mode = input_offers("your")
        their_offers, their_weight_mode = input_offers("their")

        use_weight = your_weight_mode

        your_val = summarize_trade(your_offers, use_weight)
        their_val = summarize_trade(their_offers, use_weight)
        result = fair_trade_result(your_val, their_val)

        st.markdown(f"### ⚖️ {result}")
        st.write(f"Your Offer Value: ₲{your_val:.2f}")
        st.write(f"Their Offer Value: ₲{their_val:.2f}")

        st.subheader("💬 Trade Messaging")
        for msg in st.session_state.messages:
            ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(msg["timestamp"]))
            st.write(f"**{msg['username']}** [{ts}]: {msg['message']}")

        new_msg = st.text_input("Send a message", key="new_msg_single")
        if st.button("Send Message (Single User)"):
            if not username:
                st.error("Enter username to send messages")
            elif not new_msg.strip():
                st.error("Message cannot be empty")
            else:
                st.session_state.messages.append({
                    "username": username,
                    "message": new_msg.strip(),
                    "timestamp": int(time.time())
                })
                st.experimental_rerun()

    elif trade_type == "Multi User":
        # --- Multi User Mode (shared SQLite DB) ---

        join_code = st.text_input("Enter Trade Code to Join or Leave Blank to Create New Trade")
        username = st.text_input("Enter your Roblox Username (required)")

        trade = None
        trade_code = None

        if join_code.strip():
            trade = get_trade(join_code.strip())
            if trade:
                trade_code = trade["code"]
            else:
                st.warning("Trade code not found, will create new trade on submit.")
        else:
            st.info("Leave code blank to create a new trade.")

        if st.button("Create New Trade") and username.strip():
            trade_code = create_trade(username.strip())
            st.success(f"Created new trade with code: {trade_code}")

        if trade_code:
            st.markdown(f"### Trade Code: `{trade_code}`")

            # Load offers and messages from DB
            your_offers = get_offers(trade_code, "your")
            their_offers = get_offers(trade_code, "their")
            messages = get_messages(trade_code)

            if not your_offers:
                your_offers = [{"crop": "Carrot", "weight": 0.0, "mutation": "None", "custom_price": None} for _ in range(3)]
            if not their_offers:
                their_offers = [{"crop": "Carrot", "weight": 0.0, "mutation": "None", "custom_price": None} for _ in range(3)]

            # Input offers
            def input_db_offers(owner, offers):
                st.subheader(f"{owner.capitalize()}'s Offer")
                use_custom = st.checkbox(f"Enable Custom Prices for {owner}", key=f"db_custom_prices_{owner}")
                use_weight = st.radio(f"Calculation Mode {owner}", ["Weight-based", "Base Price"], key=f"db_use_weight_{owner}", horizontal=True)
                is_weight = use_weight == "Weight-based"

                for i in range(3):
                    cols = st.columns([3, 2, 3, 2])
                    current_crop = offers[i]["crop"]
                    offers[i]["crop"] = cols[0].selectbox(f"Crop {owner} {i+1}", list(CROP_PRICES.keys()), index=list(CROP_PRICES.keys()).index(current_crop), key=f"db_crop_{owner}_{i}")
                    offers[i]["weight"] = cols[1].number_input(f"Weight {owner} {i+1}", min_value=0.0, step=0.1, value=offers[i]["weight"], key=f"db_weight_{owner}_{i}")
                    mut_list = SINGLE_USER_MUTATIONS if st.session_state.get(f"db_custom_prices_{owner}", False) else list(MUTATION_MULTIPLIERS.keys())
                    current_mut = offers[i]["mutation"] if offers[i]["mutation"] in mut_list else mut_list[0]
                    offers[i]["mutation"] = cols[2].selectbox(f"Mutation {owner} {i+1}", mut_list, index=mut_list.index(current_mut), key=f"db_mutation_{owner}_{i}")
                    if use_custom:
                        cp_val = offers[i]["custom_price"] if offers[i]["custom_price"] is not None else 0.0
                        offers[i]["custom_price"] = cols[3].number_input(f"Custom Price {owner} {i+1}", min_value=0.0, step=0.1, value=cp_val, key=f"db_custom_price_{owner}_{i}")
                    else:
                        offers[i]["custom_price"] = None
                return offers, is_weight

            your_offers, your_weight_mode = input_db_offers("your", your_offers)
            their_offers, their_weight_mode = input_db_offers("their", their_offers)

            use_weight = your_weight_mode

            your_val = summarize_trade(your_offers, use_weight)
            their_val = summarize_trade(their_offers, use_weight)
            result = fair_trade_result(your_val, their_val)

            st.markdown(f"### ⚖️ {result}")
            st.write(f"Your Offer Value: ₲{your_val:.2f}")
            st.write(f"Their Offer Value: ₲{their_val:.2f}")

            # Save offers back to DB
            if st.button("Save Offers"):
                save_offers(trade_code, "your", your_offers)
                save_offers(trade_code, "their", their_offers)
                st.success("Offers saved!")

            # Messages
            st.subheader("💬 Trade Messaging")
            for msg in messages:
                ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(msg["timestamp"]))
                st.write(f"**{msg['username']}** [{ts}]: {msg['message']}")

            new_msg = st.text_input("Send a message", key="new_msg_db")
            if st.button("Send Message"):
                if not username.strip():
                    st.error("Enter username to send messages")
                elif not new_msg.strip():
                    st.error("Message cannot be empty")
                else:
                    insert_message(trade_code, username.strip(), new_msg.strip())
                    st.experimental_rerun()
        else:
            st.info("Enter a valid username and trade code or create a new trade.")

# END
