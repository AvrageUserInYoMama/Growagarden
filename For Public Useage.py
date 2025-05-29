# Grow a Garden Crop Calculator & Trading Tool
import streamlit as st
import random

# -------------------- Data --------------------
CROP_PRICES = {
    "Carrot": 30, "Strawberry": 90, "Blueberry": 40, "Orange Tulip": 750,
    "Tomato": 80, "Corn": 100, "Daffodil": 60, "Raspberry": 1500, "Pear": 2000,
    "Pineapple": 3000, "Peach": 100, "Apple": 375, "Grape": 10000, "Venus Fly Trap": 15000,
    "Mango": 6500, "Dragon Fruit": 4750, "Cursed Fruit": 50000, "Soul Fruit": 10500,
    "Candy Blossom": 100000, "Lotus": 20000, "Durian": 4500, "Bamboo": 1200,
    "Coconut": 2500, "Pumpkin": 1000, "Watermelon": 1200, "Cactus": 3000,
    "Passionfruit": 8000, "Pepper": 14000, "Starfruit": 7500, "Moonflower": 6000,
    "Moonglow": 9000, "Blood Banana": 1200, "Moon Melon": 15000,
    "Beanstalk": 18000, "Moon Mango": 36000
}

PRICE_PER_KG = {
    "Carrot": 100, "Strawberry": 80, "Blueberry": 120, "Orange Tulip": 17000,
    "Tomato": 60, "Corn": 76, "Daffodil": 60, "Raspberry": 60, "Pear": 77,
    "Pineapple": 750, "Peach": 90, "Apple": 77.57, "Grape": 3300,
    "Venus Fly Trap": 1324, "Mango": 510, "Dragon Fruit": 70, "Cursed Fruit": 100,
    "Soul Fruit": 77, "Candy Blossom": 3900, "Lotus": 435, "Durian": 660,
    "Bamboo": 1051, "Coconut": 50, "Pumpkin": 60, "Watermelon": 80, "Cactus": 1110,
    "Passionfruit": 1400, "Pepper": 1850, "Starfruit": 5611, "Moonflower": 4000,
    "Moonglow": 3400, "Blood Banana": 4600, "Moon Melon": 130,
    "Beanstalk": 2344, "Moon Mango": 2277
}

MUTATION_MULTIPLIERS = {
    "Wet": 2, "Chilled": 2, "Chocolate": 2, "Moonlit": 2, "Bloodlit": 4,
    "Plasma": 5, "Frozen": 10, "Golden": 20, "Zombified": 25, "Shocked": 50,
    "Rainbow": 50, "Celestial": 120, "Disco": 125, "Twisted": 30
}

STACKABLE_MUTATIONS = {
    frozenset(["Wet", "Chilled"]): "Frozen"
}

# -------------------- Initialization --------------------
if "trades" not in st.session_state:
    st.session_state.trades = {}
if "messages" not in st.session_state:
    st.session_state.messages = {}

# -------------------- Functions --------------------
def calculate_value(name, weight, base_price, use_weight, mutations):
    mutations_set = set(mutations)
    for combo, result in STACKABLE_MUTATIONS.items():
        if combo.issubset(mutations_set):
            mutations_set.difference_update(combo)
            mutations_set.add(result)
    multiplier = sum(MUTATION_MULTIPLIERS.get(m, 0) for m in mutations_set)
    if use_weight:
        price_per_kg = PRICE_PER_KG.get(name, 0)
        return weight * price_per_kg * (1 + multiplier)
    else:
        return base_price * (1 + multiplier)

def evaluate_trade(offer1, offer2):
    diff = offer2 - offer1
    if abs(diff) < 0.1 * max(offer1, offer2):
        return "Fair"
    elif offer2 > offer1:
        return "Win"
    else:
        return "Loss"

# -------------------- Sidebar Mode --------------------
mode = st.sidebar.radio("Choose Mode", ["Calculator", "Trading"])

# -------------------- Calculator Mode --------------------
if mode == "Calculator":
    st.title("Crop Value Calculator")
    use_custom = st.checkbox("Custom Item")
    use_weight = st.radio("Calculation Method", ["Weight-based", "Base Price"])

    if use_custom:
        name = st.text_input("Custom Item Name")
        base_price = st.number_input("Custom Base Price", 0)
    else:
        name = st.selectbox("Select a Crop", list(CROP_PRICES.keys()))
        base_price = CROP_PRICES[name]

    weight = st.number_input("Weight (kg)", 0.0, format="%.2f") if use_weight == "Weight-based" else 0
    mutations = st.multiselect("Mutations", list(MUTATION_MULTIPLIERS.keys()))

    total = calculate_value(name, weight, base_price, use_weight == "Weight-based", mutations)
    st.subheader(f"Total Value: ₵{total:,.2f}")

# -------------------- Trading Mode --------------------
else:
    st.title("Trading Mode")
    st.markdown("Manage your trade and check fairness.")

    st.markdown("### Trade Setup")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.session_state.use_custom = st.checkbox("Enable Custom Items")
    with col2:
        use_weight = st.radio("Calculation", ["Weight-based", "Base Price"], horizontal=True)

    col_top = st.columns([2, 2, 2])
    with col_top[0]:
        if st.button("Generate Trade Code"):
            with st.form("username_form"):
                username = st.text_input("Enter your Roblox Username")
                submit = st.form_submit_button("Confirm")
                if submit and username:
                    code = random.randint(100000, 999999999)
                    st.session_state.trades[code] = {"user": username, "yours": [], "theirs": []}
                    st.session_state.current_trade_code = code
                    st.success(f"Trade Code: {code}")
    with col_top[1]:
        join_code = st.text_input("Enter Trade Code to Join")
    with col_top[2]:
        if st.button("Join Trade") and join_code:
            st.session_state.current_trade_code = int(join_code)

    def input_items(title, key):
        st.markdown(f"#### {title}")
        items = []
        for i in range(3):
            col = st.columns(4)
            if st.session_state.use_custom:
                name = col[0].text_input(f"Name {key}{i}", key=f"{key}_name_{i}")
                price = col[1].number_input(f"Price {key}{i}", key=f"{key}_price_{i}")
            else:
                name = col[0].selectbox(f"Crop {key}{i}", list(CROP_PRICES.keys()), key=f"{key}_crop_{i}")
                price = CROP_PRICES[name]
            weight = col[2].number_input(f"Weight {key}{i}", 0.0, key=f"{key}_wt_{i}") if use_weight == "Weight-based" else 0
            mutations = col[3].multiselect("Mutations", list(MUTATION_MULTIPLIERS.keys()), key=f"{key}_mut_{i}")
            items.append(calculate_value(name, weight, price, use_weight == "Weight-based", mutations))
        return sum(items)

    yours = input_items("Your Offer", "your")
    theirs = input_items("Their Offer", "their")

    st.markdown("### Trade Summary")
    st.write(f"Your Offer Value: ₵{yours:,.2f}")
    st.write(f"Their Offer Value: ₵{theirs:,.2f}")
    st.subheader(f"This trade is a: {evaluate_trade(yours, theirs)}")

    # Chat system if trade is joined/generated
    if "current_trade_code" in st.session_state:
        code = st.session_state.current_trade_code
        if code not in st.session_state.messages:
            st.session_state.messages[code] = []

        st.markdown("---")
        st.subheader(f"Chat for Trade Code {code}")
        for msg in st.session_state.messages[code]:
            st.markdown(f"**{msg['user']}:** {msg['text']}")

        with st.form("send_msg_form"):
            text = st.text_input("Type your message")
            send = st.form_submit_button("Send")
            if send and text:
                user = st.session_state.trades[code]["user"]
                st.session_state.messages[code].append({"user": user, "text": text.strip()})
                st.experimental_rerun()


