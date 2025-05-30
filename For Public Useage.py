import streamlit as st
import random
from typing import List

# Auto-refresh utility
from streamlit_autorefresh import st_autorefresh

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

# === Initialize session state ===

if "trades" not in st.session_state:
    st.session_state.trades = {}

if "messages" not in st.session_state:
    st.session_state.messages = {}

# Refresh every 3 seconds
st_autorefresh(interval=3000, key="refresh")

# === Utility Functions ===

def calculate_mutation_multiplier(mutations: List[str]) -> float:
    """Calculate combined mutation multiplier (multiply all)."""
    multiplier = 1.0
    for m in mutations:
        multiplier *= MUTATION_MULTIPLIERS.get(m, 1)
    return multiplier

def calculate_value(crop, weight, mutations, use_weight, custom_price=None):
    base_price = custom_price if custom_price is not None else CROP_PRICES.get(crop, 0)
    mutation_multiplier = calculate_mutation_multiplier(mutations)
    return (weight if use_weight else 1) * base_price * mutation_multiplier

def summarize_trade(offers, use_weight):
    total = 0.0
    for crop, weight, mutations, custom_price in offers:
        total += calculate_value(crop, weight, mutations, use_weight, custom_price)
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

# === Main UI ===

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
        weight = 1.0

    mutations = st.multiselect("Select Mutation(s)", list(MUTATION_MULTIPLIERS.keys()))
    value = calculate_value(item_name, weight, mutations, is_weight, item_price)
    st.success(f"Value of {item_name} = ₲{value:.2f}")

elif mode == "Trading Mode":
    st.header("🤝 Trading Mode")
    st.markdown("### ⚖️ Trade Fairness")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Trade Setup & Your Offer")
        use_custom = st.checkbox("Enable Custom Items", key="custom_items")
        username = st.text_input("Enter your Roblox Username", key="username")

        if st.button("Generate Trade Code"):
            if username:
                code = str(random.randint(100000, 999999999))
                if code not in st.session_state.trades:
                    st.session_state.trades[code] = {
                        "user": username,
                        "your_offer": [],
                        "their_offer": [],
                        "messages": []
                    }
                    st.success(f"Trade Code generated: {code}")
                else:
                    st.warning("Try again, code collision occurred!")

        join_code = st.text_input("Enter Trade Code to Join", key="join_code")
        if st.button("Join Trade"):
            if join_code in st.session_state.trades:
                st.success(f"Joined trade {join_code}!")
            else:
                st.error("Invalid trade code!")

        use_weight = st.radio("Calculation Method", ["Weight-based", "Base Price"], horizontal=True)
        is_weight = use_weight == "Weight-based"

        def input_offer(prefix):
            crops = []
            for i in range(3):
                cols = st.columns([3, 1.5, 3, 1.5])
                crop = cols[0].selectbox(f"Crop {prefix}{i+1}", list(CROP_PRICES.keys()), key=f"crop_{prefix}{i}")
                weight = cols[1].number_input(f"Weight {prefix}{i+1}", min_value=0.0, step=0.1, key=f"wt_{prefix}{i}")
                mutations = cols[2].multiselect(f"Mutations {prefix}{i+1}", list(MUTATION_MULTIPLIERS.keys()), key=f"mut_{prefix}{i}")
                if use_custom:
                    custom_price = cols[3].number_input(f"Custom Price {prefix}{i+1}", min_value=0.0, step=0.1, key=f"price_{prefix}{i}")
                else:
                    custom_price = None
                crops.append((crop, weight, mutations, custom_price))
            return crops

        your_offer = input_offer("your")

        # Save your offer into the trade if trade code is valid
        if join_code in st.session_state.trades:
            st.session_state.trades[join_code]["your_offer"] = your_offer
            st.session_state.trades[join_code]["user"] = username

        with col2:
            st.subheader("Their Offer (Read-Only)")
            if join_code in st.session_state.trades:
                their_offer = st.session_state.trades[join_code].get("their_offer", [])
                if not their_offer:
                    st.info("Waiting for the other party to add their offer.")
                else:
                    for i, (crop, weight, mutations, custom_price) in enumerate(their_offer):
                        st.markdown(f"**Crop {i+1}:** {crop}")
                        st.markdown(f"- Weight: {weight}")
                        st.markdown(f"- Mutations: {', '.join(mutations) if mutations else 'None'}")
                        if custom_price is not None:
                            st.markdown(f"- Custom Price: ₲{custom_price}")
                        else:
                            st.markdown(f"- Base Price: ₲{CROP_PRICES.get(crop,0)}")

        if join_code in st.session_state.trades:
            their_offer = st.session_state.trades[join_code].get("their_offer", [])
            your_val = summarize_trade(your_offer, is_weight)
            their_val = summarize_trade(their_offer, is_weight)
            result = fair_trade_result(your_val, their_val)
            st.markdown(f"### ⚖️ Trade Result: {result}")
            st.write(f"Your Offer Value: ₲{your_val:.2f}")
            st.write(f"Their Offer Value: ₲{their_val:.2f}")

            # Messages
            st.subheader("💬 Trade Messaging")

            # Initialize messages for this code if missing
            if join_code not in st.session_state.messages:
                st.session_state.messages[join_code] = []

            # Display messages
            for msg in st.session_state.messages[join_code]:
                st.write(f"🗨️ {msg}")

            new_msg = st.text_input("Send a message", key="new_msg")
            if st.button("Send Message"):
                if new_msg:
                    st.session_state.messages[join_code].append(f"{username}: {new_msg}")
                    st.experimental_rerun()

else:
    st.warning("Please select a mode.")

