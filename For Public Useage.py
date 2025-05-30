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
    "Shiny": 2.5,
    "Golden": 5,
    "Mutated": 1.5,
    "Legendary": 10,
    "Rare": 3,
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

# --- Session state initialization ---

if "trades" not in st.session_state:
    st.session_state.trades = {}  # trade_code: {user, your_offer, their_offer, messages}

if "messages" not in st.session_state:
    st.session_state.messages = {}  # trade_code: [messages]

if "current_trade_code" not in st.session_state:
    st.session_state.current_trade_code = None

if "calculator_results" not in st.session_state:
    st.session_state.calculator_results = None

# --- Auto-refresh every 3 seconds for chat/trade update ---
st_autorefresh(interval=3000, key="refresh")

# --- UI ---

st.title("🌱 Grow a Garden Crop Calculator & Trade Platform")

mode = st.radio("Choose Mode", ["Calculator Mode", "Trading Mode"], horizontal=True)

# ----------------- Calculator Mode -----------------

if mode == "Calculator Mode":
    st.header("🧮 Crop Calculator")

    use_weight = st.radio("Calculate using:", ["Weight-based (kg)", "Base Price"], horizontal=True)
    is_weight = use_weight == "Weight-based (kg)"

    st.info("Add crops with their weight, mutations, and optionally custom price.")

    crops_data = []
    add_more = True
    idx = 1
    while add_more:
        st.markdown(f"### Crop #{idx}")
        crop = st.selectbox(f"Select Crop #{idx}", list(CROP_PRICES.keys()), key=f"calc_crop_{idx}")
        weight = 0.0
        if is_weight:
            weight = st.number_input(f"Weight (kg) #{idx}", min_value=0.0, step=0.1, key=f"calc_weight_{idx}")
        mutations = st.multiselect(f"Mutations #{idx}", list(MUTATION_MULTIPLIERS.keys()), key=f"calc_mutations_{idx}")
        custom_price = st.number_input(f"Custom Price (₲) #{idx} (leave 0 to ignore)", min_value=0.0, step=0.1, key=f"calc_custom_price_{idx}")
        custom_price = custom_price if custom_price > 0 else None

        crops_data.append((crop, weight, mutations, custom_price))

        add_more = st.checkbox("Add another crop?", value=False if idx >= 1 else True, key=f"calc_add_more_{idx}")
        idx += 1
        if not add_more:
            break

    if st.button("Calculate Total Value"):
        total_value = summarize_trade(crops_data, is_weight)
        st.session_state.calculator_results = total_value

    if st.session_state.calculator_results is not None:
        st.success(f"Total Crop Value: ₲{st.session_state.calculator_results:.2f}")

# ----------------- Trading Mode -----------------

elif mode == "Trading Mode":
    st.header("🤝 Trading Mode")

    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader("Setup & Your Offer")

        username = st.text_input("Enter your Roblox Username", key="username")

        use_custom = st.checkbox("Enable Custom Prices", key="custom_items")

        use_weight = st.radio("Calculation Method", ["Weight-based", "Base Price"], horizontal=True)
        is_weight = use_weight == "Weight-based"

        # Trade code generation & joining logic
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
            # Show trade code if no one joined yet
            if not joined:
                st.info(f"Your Trade Code: **{existing_code}** (share this code to let others join!)")
            else:
                st.success(f"Trade code {existing_code} - Someone joined!")

        join_code = st.text_input("Enter Trade Code to Join", key="join_code")
        if st.button("Join Trade"):
            if join_code in st.session_state.trades:
                st.session_state.current_trade_code = join_code
                st.success(f"Joined trade {join_code}!")
            else:
                st.error("Invalid trade code!")

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
   elif mode == "Trading Mode":
    st.header("🤝 Trading Mode")

    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader("Setup & Your Offer")

        username = st.text_input("Enter your Roblox Username", key="username")

        use_custom = st.checkbox("Enable Custom Prices", key="custom_items")

        use_weight = st.radio("Calculation Method", ["Weight-based", "Base Price"], horizontal=True)
        is_weight = use_weight == "Weight-based"

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
            if not joined:
                st.info(f"Your Trade Code: **{existing_code}** (share this code to let others join!)")
            else:
                st.success(f"Trade code {existing_code} - Someone joined!")

        join_code = st.text_input("Enter Trade Code to Join", key="join_code")
        if st.button("Join Trade"):
            if join_code in st.session_state.trades:
                st.session_state.current_trade_code = join_code
                st.success(f"Joined trade {join_code}!")
            else:
                st.error("Invalid trade code!")

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
                        if use_custom and custom_price:
                            st.markdown(f"- Custom Price: ₲{custom_price}")

            # Show trade values & fairness
            your_value = summarize_trade(your_offer, is_weight)
            their_value = summarize_trade(st.session_state.trades[current_code].get("their_offer", []), is_weight)
            st.markdown(f"### Your Offer Value: ₲{your_value:.2f}")
            st.markdown(f"### Their Offer Value: ₲{their_value:.2f}")
            st.markdown(f"### Trade Result: {fair_trade_result(your_value, their_value)}")
