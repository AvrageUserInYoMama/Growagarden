import streamlit as st
import random
from typing import List, Tuple
from streamlit_autorefresh import st_autorefresh

# --- Constants ---

CROP_PRICES = {
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
    "Shiny": 2.5,
    "Golden": 5,
    "Mutated": 1.5,
    "Legendary": 10,
    "Rare": 3,
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

# --- Helper functions ---

def calculate_crop_value(crop: str, weight: float, mutations: List[str], use_weight: bool, custom_price: float = None) -> float:
    base_price = custom_price if custom_price is not None else CROP_PRICES.get(crop, 0)
    price_per_kg = PRICE_PER_KG.get(crop, 0)
    multiplier = 1.0
    for m in mutations:
        multiplier *= MUTATION_MULTIPLIERS.get(m, 1)
    if use_weight:
        value = weight * price_per_kg * multiplier
    else:
        value = base_price * multiplier
    return value

def summarize_trade(offer: List[Tuple[str, float, List[str], float]], use_weight: bool) -> float:
    total = 0.0
    for crop, weight, mutations, custom_price in offer:
        total += calculate_crop_value(crop, weight, mutations, use_weight, custom_price)
    return total

def fair_trade_result(your_val: float, their_val: float) -> str:
    if abs(your_val - their_val) < 1e-2:
        return "Fair Trade 🤝"
    elif your_val > their_val:
        return "You Win! 🎉"
    else:
        return "You Lose 😢"

# --- Initialize session state ---

if "trades" not in st.session_state:
    st.session_state.trades = {}  # trade_code: {user, your_offer, their_offer, messages}

if "messages" not in st.session_state:
    st.session_state.messages = {}  # trade_code: [messages]

if "current_trade_code" not in st.session_state:
    st.session_state.current_trade_code = None

# --- Auto refresh chat and trade info every 3 seconds ---
st_autorefresh(interval=3000, key="refresh")

# --- UI ---

st.title("🌱 Grow a Garden Trade Calculator")

mode = st.radio("Choose Mode", ["Calculator Mode", "Trading Mode"], horizontal=True)

if mode == "Calculator Mode":
    st.header("Calculator Mode")
    # Place your calculator mode code here
    st.info("Calculator Mode is not implemented in this snippet, please add your calculator code.")

elif mode == "Trading Mode":
    st.header("🤝 Trading Mode")

    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader("Trade Setup & Your Offer")

        username = st.text_input("Enter your Roblox Username", key="username")

        use_custom = st.checkbox("Enable Custom Prices", key="custom_items")

        use_weight = st.radio("Calculation Method", ["Weight-based", "Base Price"], horizontal=True)
        is_weight = use_weight == "Weight-based"

        # Show trade code and allow generation/joining
        existing_code = st.session_state.current_trade_code
        joined = False
        if existing_code:
            trade = st.session_state.trades.get(existing_code)
            if trade and trade.get("their_offer"):
                joined = True

        if not existing_code or joined:
            if st.button("Generate Trade Code"):
                if username:
                    code = str(random.randint(100000, 999999999))
                    while code in st.session_state.trades:
                        code = str(random.randint(100000, 999999999))
                    st.session_state.trades[code] = {
                        "user": username,
                        "your_offer": [],
                        "their_offer": [],
                        "messages": [],
                    }
                    st.session_state.current_trade_code = code
                    st.success(f"Trade Code generated: {code}")
                else:
                    st.error("Please enter your username before generating a trade code.")
        else:
            st.info(f"Your Trade Code: **{existing_code}** (share this to let others join!)")

        join_code = st.text_input("Enter Trade Code to Join", key="join_code")
        if st.button("Join Trade"):
            if join_code in st.session_state.trades:
                st.session_state.current_trade_code = join_code
                st.success(f"Joined trade {join_code}!")
            else:
                st.error("Invalid trade code!")

        # Input offer helper function
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

        current_code = st.session_state.current_trade_code

        if current_code:
            your_offer = input_offer("your")

            # Save your offer and username
            st.session_state.trades[current_code]["your_offer"] = your_offer
            st.session_state.trades[current_code]["user"] = username

            with col2:
                st.subheader("Their Offer (Read-Only)")
                their_offer = st.session_state.trades[current_code].get("their_offer", [])
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
                            st.markdown(f"- Base Price: ₲{CROP_PRICES.get(crop, 0)}")

            # Show trade values and fairness
            their_offer = st.session_state.trades[current_code].get("their_offer", [])
            your_val = summarize_trade(st.session_state.trades[current_code]["your_offer"], is_weight)
            their_val = summarize_trade(their_offer, is_weight)
            result = fair_trade_result(your_val, their_val)

            st.markdown(f"### ⚖️ Trade Result: {result}")
            st.write(f"Your Offer Value: ₲{your_val:.2f}")
            st.write(f"Their Offer Value: ₲{their_val:.2f}")

            # Messaging system
            st.subheader("💬 Trade Messaging")

            if current_code not in st.session_state.messages:
                st.session_state.messages[current_code] = []

            # Display messages
            for msg in st.session_state.messages[current_code]:
                st.write(f"🗨️ {msg}")

            new_msg = st.text_input("Send a message", key="new_msg")
            if st.button("Send Message"):
                if new_msg:
                    st.session_state.messages[current_code].append(f"{username}: {new_msg}")
                    # Refresh immediately to show new message
                    st.experimental_rerun()

        else:
            st.info("Generate or join a trade to start.")

