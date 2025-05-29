import streamlit as st
import sqlite3
import random
import time

# --- Database Setup & Helpers ---

DB_FILE = "trades.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    # Trades table: stores trade code, username
    c.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            code TEXT PRIMARY KEY,
            username TEXT NOT NULL
        )
    ''')
    # Offers table: stores trade offers with crop details, belongs to a trade
    c.execute('''
        CREATE TABLE IF NOT EXISTS offers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trade_code TEXT NOT NULL,
            owner TEXT NOT NULL,  -- "your" or "their"
            crop TEXT NOT NULL,
            weight REAL NOT NULL,
            mutation TEXT NOT NULL,
            custom_price REAL,
            FOREIGN KEY(trade_code) REFERENCES trades(code)
        )
    ''')
    # Messages table: stores messages per trade
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trade_code TEXT NOT NULL,
            username TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp INTEGER NOT NULL,
            FOREIGN KEY(trade_code) REFERENCES trades(code)
        )
    ''')
    conn.commit()
    conn.close()

# Initialize DB on app start
init_db()

# --- Crop Prices and Mutation Multipliers ---

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

# --- Calculation Functions ---

def calculate_value(crop, weight, mutation, use_weight, custom_price=None):
    base_price = custom_price if custom_price is not None else CROP_PRICES.get(crop, 0)
    mutation_multiplier = MUTATION_MULTIPLIERS.get(mutation, 1)
    return (weight if use_weight else 1) * base_price * mutation_multiplier

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

# --- DB Access Functions ---

def insert_trade(code, username):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO trades (code, username) VALUES (?, ?)", (code, username))
        conn.commit()
    except sqlite3.IntegrityError:
        # code already exists
        conn.close()
        return False
    conn.close()
    return True

def get_trade(code):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM trades WHERE code=?", (code,))
    trade = c.fetchone()
    conn.close()
    return trade

def insert_offer(trade_code, owner, crop, weight, mutation, custom_price):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        '''
        INSERT INTO offers (trade_code, owner, crop, weight, mutation, custom_price)
        VALUES (?, ?, ?, ?, ?, ?)
        ''',
        (trade_code, owner, crop, weight, mutation, custom_price),
    )
    conn.commit()
    conn.close()

def get_offers(trade_code, owner):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "SELECT crop, weight, mutation, custom_price FROM offers WHERE trade_code=? AND owner=?",
        (trade_code, owner),
    )
    offers = c.fetchall()
    conn.close()
    # Return list of dicts for convenience
    return [
        {
            "crop": row["crop"],
            "weight": row["weight"],
            "mutation": row["mutation"],
            "custom_price": row["custom_price"],
        }
        for row in offers
    ]

def delete_offers(trade_code, owner):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM offers WHERE trade_code=? AND owner=?", (trade_code, owner))
    conn.commit()
    conn.close()

def insert_message(trade_code, username, message):
    conn = get_db_connection()
    c = conn.cursor()
    timestamp = int(time.time())
    c.execute(
        "INSERT INTO messages (trade_code, username, message, timestamp) VALUES (?, ?, ?, ?)",
        (trade_code, username, message, timestamp),
    )
    conn.commit()
    conn.close()

def get_messages(trade_code):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT username, message, timestamp FROM messages WHERE trade_code=? ORDER BY timestamp ASC", (trade_code,))
    msgs = c.fetchall()
    conn.close()
    return msgs

# --- Streamlit App ---

st.set_page_config(page_title="Grow a Garden Trade Calculator", layout="wide")

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

    mutation = st.selectbox("Select Mutation", list(MUTATION_MULTIPLIERS.keys()))

    value = calculate_value(item_name, weight, mutation, is_weight, item_price)
    st.success(f"Value of {item_name} = ₲{value:.2f}")

elif mode == "Trading Mode":
    st.header("🤝 Trading Mode")
    st.markdown("### ⚖️ Trade Fairness")

    # Trade setup and joining
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Trade Setup")
        username = st.text_input("Enter your Roblox Username", key="username_trade")
        if st.button("Generate Trade Code"):
            if not username:
                st.error("Please enter your username first!")
            else:
                # Generate unique 9-digit code
                for _ in range(10):
                    code = str(random.randint(100000000, 999999999))
                    if insert_trade(code, username):
                        st.success(f"Trade Code Generated: {code}")
                        st.session_state.trade_code = code
                        break
                else:
                    st.error("Could not generate unique trade code, try again.")

    with col2:
        st.subheader("Join Trade")
        join_code = st.text_input("Paste trade code here to join")
        if st.button("Join Trade"):
            trade = get_trade(join_code)
            if trade is None:
                st.error("Invalid trade code")
            else:
                st.success(f"Joined trade {join_code}")
                st.session_state.trade_code = join_code

    # If no trade_code in session, show message and stop here
    if "trade_code" not in st.session_state:
        st.info("Generate or join a trade above to continue.")
        st.stop()

    trade_code = st.session_state.trade_code

    # Use weight or base price
    use_weight = st.radio("Calculation Method", ["Weight-based", "Base Price"], horizontal=True)
    is_weight = use_weight == "Weight-based"

    # Option to enable custom prices for offers
    use_custom = st.checkbox("Enable Custom Prices for Items", key="custom_prices_checkbox")

    st.markdown("---")

    # Input offers: your offer and their offer
    def trade_input_section(owner_prefix):
        st.subheader(f"{owner_prefix.capitalize()}'s Offer")

        # Clear existing offers inputs on first load
        if f"offers_{owner_prefix}_loaded" not in st.session_state:
            st.session_state[f"offers_{owner_prefix}_loaded"] = False

        if not st.session_state[f"offers_{owner_prefix}_loaded"]:
            # Load offers from DB if exists
            offers_db = get_offers(trade_code, owner_prefix)
            # If none, pre-fill empty offers
            if not offers_db:
                offers_db = [
                    {"crop": list(CROP_PRICES.keys())[0], "weight": 0.0, "mutation": list(MUTATION_MULTIPLIERS.keys())[0], "custom_price": None},
                    {"crop": list(CROP_PRICES.keys())[0], "weight": 0.0, "mutation": list(MUTATION_MULTIPLIERS.keys())[0], "custom_price": None},
                    {"crop": list(CROP_PRICES.keys())[0], "weight": 0.0, "mutation": list(MUTATION_MULTIPLIERS.keys())[0], "custom_price": None},
                ]
            st.session_state[f"offers_{owner_prefix}"] = offers_db
            st.session_state[f"offers_{owner_prefix}_loaded"] = True

        offers = st.session_state[f"offers_{owner_prefix}"]

        # Display inputs
        for i in range(3):
            cols = st.columns([3, 2, 3, 2])
            offers[i]["crop"] = cols[0].selectbox(f"Crop {owner_prefix} {i+1}", list(CROP_PRICES.keys()), index=list(CROP_PRICES.keys()).index(offers[i]["crop"]), key=f"crop_{owner_prefix}_{i}")
            offers[i]["weight"] = cols[1].number_input(f"Weight {owner_prefix} {i+1}", min_value=0.0, step=0.1, value=offers[i]["weight"], key=f"weight_{owner_prefix}_{i}")
            offers[i]["mutation"] = cols[2].selectbox(f"Mutation {owner_prefix} {i+1}", list(MUTATION_MULTIPLIERS.keys()), index=list(MUTATION_MULTIPLIERS.keys()).index(offers[i]["mutation"]), key=f"mutation_{owner_prefix}_{i}")
            if use_custom:
                # Use 0.0 as default if None
                cp_val = offers[i]["custom_price"] if offers[i]["custom_price"] is not None else 0.0
                offers[i]["custom_price"] = cols[3].number_input(f"Custom Price {owner_prefix} {i+1}", min_value=0.0, step=0.1, value=cp_val, key=f"custom_price_{owner_prefix}_{i}")
            else:
                offers[i]["custom_price"] = None

        st.session_state[f"offers_{owner_prefix}"] = offers

    # Show trade inputs for both users
    trade_input_section("your")
    trade_input_section("their")

    # Save offers to DB button
    if st.button("Save Offers"):
        # Delete old offers
        delete_offers(trade_code, "your")
        delete_offers(trade_code, "their")

        # Insert current offers
        for offer in st.session_state["offers_your"]:
            insert_offer(trade_code, "your", offer["crop"], offer["weight"], offer["mutation"], offer["custom_price"])
        for offer in st.session_state["offers_their"]:
            insert_offer(trade_code, "their", offer["crop"], offer["weight"], offer["mutation"], offer["custom_price"])
        st.success("Offers saved!")

    # Load offers from DB for calculation (always fresh)
    your_offers_db = get_offers(trade_code, "your")
    their_offers_db = get_offers(trade_code, "their")

    your_val = summarize_trade(your_offers_db, is_weight)
    their_val = summarize_trade(their_offers_db, is_weight)
    result = fair_trade_result(your_val, their_val)

    st.markdown(f"### ⚖️ {result}")

    st.subheader("Trade Summary")
    st.write(f"Your Offer Value: ₲{your_val:.2f}")
    st.write(f"Their Offer Value: ₲{their_val:.2f}")

    # --- Messaging Section ---

    st.subheader("💬 Trade Messaging")

    messages = get_messages(trade_code)
    for msg in messages:
        ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(msg["timestamp"]))
        st.write(f"**{msg['username']}** [{ts}]: {msg['message']}")

    new_msg = st.text_input("Send a message", key="new_message")
    if st.button("Send Message"):
        if "username_trade" not in st.session_state or not st.session_state.username_trade:
            st.error("Please enter your username before sending messages!")
        elif not new_msg.strip():
            st.error("Message cannot be empty!")
        else:
            insert_message(trade_code, st.session_state.username_trade, new_msg.strip())
            st.experimental_rerun()  # Refresh to show new message
