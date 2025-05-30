import streamlit as st
import sqlite3

# === DATA SETUP ===

BASE_PRICES = {
    "Carrot": 100, "Strawberry": 80, "Blueberry": 120, "Orange Tulip": 17000, "Tomato": 60, "Corn": 76,
    "Daffodil": 60, "Raspberry": 60, "Pear": 77, "Pineapple": 750, "Peach": 90, "Apple": 77.57, "Grape": 3300,
    "Venus Fly Trap": 1324, "Mango": 510, "Dragon Fruit": 70, "Cursed Fruit": 100, "Soul Fruit": 77,
    "Candy Blossom": 3900, "Lotus": 435, "Durian": 660, "Bamboo": 1051, "Coconut": 50, "Pumpkin": 60,
    "Watermelon": 80, "Cactus": 1110, "Passionfruit": 1400, "Pepper": 1850, "Starfruit": 5611,
    "Moonflower": 4000, "Moonglow": 3400, "Blood Banana": 4600, "Moon Melon": 130, "Beanstalk": 2344,
    "Moon Mango": 2277,
}

PRICE_PER_KG = BASE_PRICES.copy()

MUTATION_MULTIPLIERS = {
    "None": 1,
    "Wet": 2, "Chilled": 2, "Chocolate": 2, "Moonlit": 2, "Bloodlit": 4,
    "Plasma": 5, "Frozen": 10, "Golden": 20, "Zombified": 25, "Shocked": 50,
    "Rainbow": 50, "Celestial": 120, "Disco": 125, "Twisted": 30, "Pollinated": 2,
}

# === FUNCTIONS ===

def calculate_crop_value(crop, weight, mutations):
    base = PRICE_PER_KG.get(crop, 0)
    multiplier = 1
    for m in mutations:
        multiplier *= MUTATION_MULTIPLIERS.get(m, 1)
    return base * weight * multiplier

def save_trade_to_db(offer1, offer2):
    with sqlite3.connect("trades.db") as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS trades (offer1 TEXT, offer2 TEXT)''')
        c.execute("INSERT INTO trades (offer1, offer2) VALUES (?, ?)", (str(offer1), str(offer2)))
        conn.commit()

def load_trade_history():
    with sqlite3.connect("trades.db") as conn:
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS trades (offer1 TEXT, offer2 TEXT)")
        c.execute("SELECT * FROM trades")
        return c.fetchall()

# === STREAMLIT UI ===

st.set_page_config(page_title="Grow a Garden Calculator & Trading", layout="wide")
st.title("🌱 Grow a Garden Calculator & Trade Tool")

section = st.sidebar.radio("Navigate", ["Calculator", "Trading", "Values"])

# === CALCULATOR SECTION ===

if section == "Calculator":
    st.header("Crop Value Calculator")

    crop = st.selectbox("Select Crop", list(BASE_PRICES.keys()))
    weight = st.number_input("Enter weight (kg)", min_value=0.0, step=0.1)
    mutations = []
    for i in range(10):
        m = st.selectbox(f"Mutation {i+1}", list(MUTATION_MULTIPLIERS.keys()), key=f"mut{i}")
        if m != "None":
            mutations.append(m)

    if st.button("Calculate Value"):
        value = calculate_crop_value(crop, weight, mutations)
        st.success(f"💰 Total Value for {weight}kg of {crop}: {value:,.2f} coins")

# === TRADING SECTION ===

elif section == "Trading":
    st.header("Two-Person Crop Trading Evaluator")

    col1, col2 = st.columns(2)
    offer1, offer2 = [], []

    with col1:
        st.subheader("Trader 1 Offer")
        for i in range(3):
            crop = st.selectbox(f"Crop {i+1}", list(BASE_PRICES.keys()), key=f"t1crop{i}")
            weight = st.number_input(f"Weight {i+1} (kg)", min_value=0.0, step=0.1, key=f"t1w{i}")
            mutations = []
            for m in range(3):
                mut = st.selectbox(f"Mut {i+1}-{m+1}", list(MUTATION_MULTIPLIERS.keys()), key=f"t1mut{i}{m}")
                if mut != "None":
                    mutations.append(mut)
            offer1.append((crop, weight, mutations))

    with col2:
        st.subheader("Trader 2 Offer")
        for i in range(3):
            crop = st.selectbox(f"Crop {i+1}", list(BASE_PRICES.keys()), key=f"t2crop{i}")
            weight = st.number_input(f"Weight {i+1} (kg)", min_value=0.0, step=0.1, key=f"t2w{i}")
            mutations = []
            for m in range(3):
                mut = st.selectbox(f"Mut {i+1}-{m+1}", list(MUTATION_MULTIPLIERS.keys()), key=f"t2mut{i}{m}")
                if mut != "None":
                    mutations.append(mut)
            offer2.append((crop, weight, mutations))

    if st.button("Evaluate Trade"):
        total1 = sum(calculate_crop_value(c, w, m) for c, w, m in offer1)
        total2 = sum(calculate_crop_value(c, w, m) for c, w, m in offer2)
        save_trade_to_db(offer1, offer2)

        st.markdown(f"**Trader 1 Total:** {total1:,.2f} coins")
        st.markdown(f"**Trader 2 Total:** {total2:,.2f} coins")

        diff = abs(total1 - total2)
        if diff < 100:
            st.success("✅ Fair Trade")
        else:
            winner = "Trader 1" if total1 > total2 else "Trader 2"
            st.warning(f"⚠️ Uneven Trade! {winner} is ahead by {diff:,.2f} coins")

    with st.expander("📜 Past Trades"):
        for row in load_trade_history():
            st.markdown(f"- **Trader 1:** {row[0]} | **Trader 2:** {row[1]}")

# === VALUES SECTION ===

elif section == "Values":
    st.header("📈 Crop Prices and Mutations")

    st.subheader("Price per KG")
    st.dataframe(PRICE_PER_KG.items(), use_container_width=True)

    st.subheader("Mutation Multipliers")
    st.dataframe(MUTATION_MULTIPLIERS.items(), use_container_width=True)

    st.caption("Grow a Garden Full Version © 2025")


