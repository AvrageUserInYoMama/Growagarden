import streamlit as st
import random

st.set_page_config(page_title="Grow a Garden Trade Calculator", layout="wide")

# === Full Crop Prices (base price per item) ===
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

# === Price per kilogram ===
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

# === Mutation multipliers ===
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

# === Session State Init ===
if "messages" not in st.session_state:
    st.session_state.messages = []
if "trades" not in st.session_state:
    st.session_state.trades = {}

# === Utility Functions ===

def calculate_value(crop, weight, mutation, use_weight, custom_price=None):
    """Calculate value of crop, applying weight and mutation multiplier."""
    # Determine base price based on calculation mode
    if use_weight:
        base_price = PRICE_PER_KG.get(crop, 0)
    else:
        base_price = CROP_PRICES.get(crop, 0)

    # Override with custom price if given
    if custom_price is not None:
        base_price = custom_price

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

    mutation = st.selectbox("Select Mutation", ["None"] + list(MUTATION_MULTIPLIERS.keys()))

    # If mutation = None, multiplier = 1
    if mutation == "None":
        mutation = None

    value = calculate_value(item_name, weight, mutation, is_weight, item_price)
    st.success(f"Value of {item_name} = ₲{value:.2f}")

elif mode == "Trading Mode":
    st.header("🤝 Trading Mode")
    st.markdown("### ⚖️ Trade Fairness")

    with st.container():
        col1, col2 = st.columns([3, 3])

        with col1:
            st.subheader("Trade Setup")
            use_custom = st.checkbox("Enable Custom Items")
            username = st.text_input("Enter your Roblox Username", key="gen_user")
            if st.button("Generate Trade Code"):
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
        crops = []
        for i in range(3):
            cols = st.columns([2, 1, 2, 1])
            crop = cols[0].selectbox(f"Crop {prefix}{i}", list(CROP_PRICES.keys()), key=f"crop_{prefix}{i}")
            weight = cols[1].number_input(f"Weight {prefix}{i}", min_value=0.0, step=0.1, key=f"wt_{prefix}{i}")
            mutation = cols[2].selectbox("Mutation", ["None"] + list(MUTATION_MULTIPLIERS.keys()), key=f"mut_{prefix}{i}")
            if mutation == "None":
                mutation = None
            if use_custom:
                custom_price = cols[3].number_input("Custom Price", min_value=0.0, step=0.1, key=f"price_{prefix}{i}")
            else:
                custom_price = None
            crops.append((crop, weight, mutation, custom_price))
        return crops

    your_offer = trade_inputs("your")
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
