import streamlit as st
import random
import sqlite3
from contextlib import closing

# === Constants ===

CROP_PRICES = {
    # Add all your crops with base prices here
    "Carrot": 30,
    "Strawberry": 90,
    "Tomato": 45,
    "Potato": 25,
    "Corn": 40,
    "Cucumber": 35,
    # Add more as needed...
}

MUTATION_MULTIPLIERS = {
    "Normal": 1,
    "Wet": 2,
    "Chilled": 2,
    "Juicy": 2,
    "Dry": 0.5,
    "Rotten": 0.2,
    # Add more if needed...
}

DB_PATH = "grow_a_garden.db"

# === Database helpers ===

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with closing(get_db_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            code TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            mode TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS offers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trade_code TEXT NOT NULL,
            side TEXT NOT NULL,
            crop TEXT NOT NULL,
            weight REAL NOT NULL,
            mutation TEXT NOT NULL,
            custom_price REAL,
            FOREIGN KEY(trade_code) REFERENCES trades(code)
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trade_code TEXT NOT NULL,
            username TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(trade_code) REFERENCES trades(code)
        );
        """)
        conn.commit()

def insert_trade(code, username, mode):
    with closing(get_db_connection()) as conn:
        conn.execute(
            "INSERT INTO trades (code, username, mode) VALUES (?, ?, ?)",
            (code, username, mode)
        )
        conn.commit()

def get_trade(code):
    with closing(get_db_connection()) as conn:
        trade = conn.execute("SELECT * FROM trades WHERE code = ?", (code,)).fetchone()
        return trade

def insert_offer(code, side, crop, weight, mutation, custom_price):
    with closing(get_db_connection()) as conn:
        conn.execute("""
            INSERT INTO offers (trade_code, side, crop, weight, mutation, custom_price)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (code, side, crop, weight, mutation, custom_price))
        conn.commit()

def get_offers(code, side):
    with closing(get_db_connection()) as conn:
        rows = conn.execute("""
            SELECT * FROM offers WHERE trade_code = ? AND side = ?
        """, (code, side)).fetchall()
        return rows

def delete_offers(code, side):
    with closing(get_db_connection()) as conn:
        conn.execute("""
            DELETE FROM offers WHERE trade_code = ? AND side = ?
        """, (code, side))
        conn.commit()

def insert_message(code, username, message):
    with closing(get_db_connection()) as conn:
        conn.execute("""
            INSERT INTO messages (trade_code, username, message) VALUES (?, ?, ?)
        """, (code, username, message))
        conn.commit()

def get_messages(code):
    with closing(get_db_connection()) as conn:
        rows = conn.execute("""
            SELECT * FROM messages WHERE trade_code = ? ORDER BY timestamp
        """, (code,)).fetchall()
        return rows

# === Calculation helpers ===

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
            offer["custom_price"]
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

# === Initialize DB ===
init_db()

# === Streamlit UI ===

st.title("🌱 Grow a Garden Crop Calculator & Trade Platform")

mode = st.radio("Select Mode:", ["Calculator Mode", "Trading Mode"], horizontal=True)

if mode == "Calculator Mode":
    st.header("🔢 Crop Calculator")
    # Simple calculator example for single crop input
    crop = st.selectbox("Select Crop", list(CROP_PRICES.keys()))
    weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1)
    mutation = st.selectbox("Select Mutation", list(MUTATION_MULTIPLIERS.keys()))
    use_weight = st.checkbox("Calculate using weight", value=True)

    custom_price = st.number_input("Custom price (optional, ₲)", min_value=0.0, step=0.1)

    value = calculate_value(crop, weight, mutation, use_weight, custom_price if custom_price > 0 else None)
    st.write(f"Estimated Value: ₲{value:.2f}")

elif mode == "Trading Mode":
    st.header("🤝 Trading Mode")

    with st.form("trade_setup_form"):
        username = st.text_input("Your Roblox Username", key="username_input")
        trade_mode = st.selectbox("Trade Mode", ["1 person", "2 people"])
        generate = st.form_submit_button("Generate Trade Code")
    if generate:
        if username:
            code = str(random.randint(100000, 999999))
            insert_trade(code, username, trade_mode)
            st.success(f"Trade Code Generated: {code}")
            st.session_state.current_trade_code = code
            st.session_state.current_username = username
            st.session_state.trade_mode = trade_mode
        else:
            st.error("Please enter your username before generating a trade code.")

    join_code = st.text_input("Enter Trade Code to Join", key="join_code")
    join = st.button("Join Trade")
    if join:
        trade = get_trade(join_code)
        if trade:
            st.session_state.current_trade_code = join_code
            st.session_state.current_username = username or "Guest"
            st.session_state.trade_mode = trade["mode"]
            st.success(f"Joined trade {join_code}!")
        else:
            st.error("Invalid trade code.")

    # If joined a trade, show offers & chat
    if "current_trade_code" in st.session_state:
        code = st.session_state.current_trade_code
        username = st.session_state.get("current_username", "Guest")
        trade_mode = st.session_state.get("trade_mode", "2 people")

        st.subheader(f"Trade Code: {code} | Mode: {trade_mode}")

        use_weight = st.radio("Calculation Method", ["Weight-based", "Base Price"], horizontal=True)
        is_weight = use_weight == "Weight-based"

        # Your offer input form
        st.markdown("### Your Offer")
        with st.form("your_offer_form"):
            delete_offers(code, "your")
            your_crops = []
            for i in range(3):
                cols = st.columns([3, 2, 3, 2])
                crop = cols[0].selectbox(f"Crop {i+1}", list(CROP_PRICES.keys()), key=f"your_crop_{i}")
                weight = cols[1].number_input(f"Weight {i+1}", min_value=0.0, step=0.1, key=f"your_weight_{i}")
                mutation = cols[2].selectbox(f"Mutation {i+1}", list(MUTATION_MULTIPLIERS.keys()), key=f"your_mut_{i}")
                custom_price = cols[3].number_input(f"Custom Price {i+1} (optional)", min_value=0.0, step=0.1, key=f"your_price_{i}")
                insert_offer(code, "your", crop, weight, mutation, custom_price if custom_price > 0 else None)
            submitted = st.form_submit_button("Save Your Offer")
            if submitted:
                st.success("Your offer saved!")

        # Their offer input form
        st.markdown("### Their Offer")
        if trade_mode == "2 people":
            with st.form("their_offer_form"):
                delete_offers(code, "their")
                for i in range(3):
                    cols = st.columns([3, 2, 3, 2])
                    crop = cols[0].selectbox(f"Crop {i+1}", list(CROP_PRICES.keys()), key=f"their_crop_{i}")
                    weight = cols[1].number_input(f"Weight {i+1}", min_value=0.0, step=0.1, key=f"their_weight_{i}")
                    mutation = cols[2].selectbox(f"Mutation {i+1}", list(MUTATION_MULTIPLIERS.keys()), key=f"their_mut_{i}")
                    custom_price = cols[3].number_input(f"Custom Price {i+1} (optional)", min_value=0.0, step=0.1, key=f"their_price_{i}")
                    insert_offer(code, "their", crop, weight, mutation, custom_price if custom_price > 0 else None)
                submitted = st.form_submit_button("Save Their Offer")
                if submitted:
                    st.success("Their offer saved!")
        else:
            st.info("Single person mode — no 'Their Offer' needed.")

        # Calculate trade result
        your_offers_db = get_offers(code, "your")
        their_offers_db = get_offers(code, "their") if trade_mode == "2 people" else []

        your_total = summarize_trade(your_offers_db, is_weight)
        their_total = summarize_trade(their_offers_db, is_weight) if their_offers_db else 0
        result = fair_trade_result(your_total, their_total)

        st.markdown(f"### ⚖️ Trade Result: {result}")
        st.write(f"Your Offer Value: ₲{your_total:.2f}")
        if trade_mode == "2 people":
            st.write(f"Their Offer Value: ₲{their_total:.2f}")

        # Trade chat
        st.subheader("💬 Trade Chat")
        new_message = st.text_input("Send a message", key="new_message")
        if st.button("Send Message", key="send_msg"):
            if new_message.strip():
                insert_message(code, username, new_message.strip())
                st.experimental_rerun()

        messages = get_messages(code)
        for msg in messages:
            st.write(f"**{msg['username']}**: {msg['message']}")

# ---- END ----
