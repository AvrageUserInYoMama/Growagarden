import streamlit as st
import random
import time

# --- Constants ---

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

st.set_page_config(page_title="🌱 Grow a Garden Trade Calculator", layout="wide")

# --- Initialize session state ---

if "trades" not in st.session_state:
    st.session_state.trades = {}

if "messages" not in st.session_state:
    st.session_state.messages = {}

if "current_code" not in st.session_state:
    st.session_state.current_code = None

if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

# --- Helper functions ---

def calculate_mutation_multiplier(mutations):
    multiplier = 1
    for mut in mutations:
        multiplier *= MUTATION_MULTIPLIERS.get(mut, 1)
    return multiplier

def calculate_value(crop, weight, mutations):
    base_price = PRICE_PER_KG.get(crop, 0)
    mult = calculate_mutation_multiplier(mutations)
    return weight * base_price * mult

def summarize_trade(offers):
    total = 0
    for crop, weight, mutations in offers:
        total += calculate_value(crop, weight, mutations)
    return total

def fair_trade_result(your_val, their_val):
    if your_val == 0 and their_val == 0:
        return "Start building your trade."
    if your_val > their_val:
        return "This trade is a Loss"
    elif your_val < their_val:
        return "This trade is a Win"
    else:
        return "This trade is Fair"

# --- UI ---

st.title("🌱 Grow a Garden Trade Calculator")

mode = st.radio("Choose Mode", ["Calculator Mode", "Trading Mode"], horizontal=True)

if mode == "Calculator Mode":
    st.header("🔢 Crop Calculator")

    crop = st.selectbox("Select Crop", list(PRICE_PER_KG.keys()))
    weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1, value=1.0)

    mutations = st.multiselect("Select Mutations (multiple allowed)", list(MUTATION_MULTIPLIERS.keys()))

    value = calculate_value(crop, weight, mutations)
    st.success(f"Value of {crop} ({weight} kg, mutations: {', '.join(mutations) if mutations else 'None'}) = ₲{value:,.2f}")

else:
    st.header("🤝 Trading Mode")

    trade_type = st.radio("Trade Type", ["1 Person (View Only)", "2 People (Interact)"], horizontal=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Trade Setup & Your Offer")
        use_custom = st.checkbox("Enable Custom Items", key="custom_items")

        username = st.text_input("Enter your Roblox Username", key="username")

        if st.button("Generate Trade Code"):
            if username.strip():
                code = str(random.randint(100000, 999999999))
                st.session_state.trades[code] = {
                    "creator": username.strip(),
                    "joined": False,
                    "joiner": None,
                    "your_offer": [("", 0.0, []) for _ in range(3)],
                    "their_offer": [("", 0.0, []) for _ in range(3)],
                    "messages": [],
                    "trade_type": trade_type,
                }
                st.session_state.current_code = code
                st.success(f"Trade Code: {code}")

    with col2:
        st.subheader("Join Trade")

        join_code = st.text_input("Enter Trade Code to Join", key="join_code")

        if st.button("Join Trade"):
            if join_code in st.session_state.trades:
                st.session_state.trades[join_code]["joined"] = True
                st.session_state.trades[join_code]["joiner"] = "JoinedUser"
                st.session_state.current_code = join_code
                st.success(f"Joined trade with code: {join_code}")
            else:
                st.error("Invalid trade code.")

    code = st.session_state.get("current_code")
    if not code or code not in st.session_state.trades:
        st.info("Generate or join a trade to start.")
        st.stop()

    trade = st.session_state.trades[code]

    st.markdown(f"### Trade Code: `{code}`")
    if not trade["joined"] and trade["trade_type"] == "2 People (Interact)":
        st.info("Waiting for someone to join this trade...")

    # Auto-refresh every 3 seconds to update chat and trades
    now = time.time()
    if now - st.session_state.last_refresh > 3:
        st.session_state.last_refresh = now
        try:
            st.experimental_rerun()
        except AttributeError:
            st.stop()

    def trade_input_area(offers, editable=True, key_prefix="your"):
        new_offer = []
        for i in range(3):
            cols = st.columns([3, 2, 4])
            crop_val = offers[i][0] if i < len(offers) else ""
            weight_val = offers[i][1] if i < len(offers) else 0.0
            muts_val = offers[i][2] if i < len(offers) else []
            if editable:
                crop = cols[0].selectbox(f"Crop {i+1}", list(PRICE_PER_KG.keys()),
                                         index=(list(PRICE_PER_KG.keys()).index(crop_val) if crop_val in PRICE_PER_KG else 0),
                                         key=f"{key_prefix}_crop_{i}")
                weight = cols[1].number_input(f"Weight {i+1}", min_value=0.0, step=0.1, value=weight_val,
                                              key=f"{key_prefix}_weight_{i}")
                mutations = cols[2].multiselect(f"Mutations {i+1}", list(MUTATION_MULTIPLIERS.keys()), default=muts_val,
                                               key=f"{key_prefix}_mut_{i}")
            else:
                crop = cols[0].text_input(f"Crop {i+1}", value=crop_val, disabled=True, key=f"{key_prefix}_crop_{i}")
                weight = cols[1].number_input(f"Weight {i+1}", min_value=0.0, step=0.1, value=weight_val, disabled=True,
                                              key=f"{key_prefix}_weight_{i}")
                muts_str = ", ".join(muts_val) if muts_val else "None"
                cols[2].text_input(f"Mutations {i+1}", value=muts_str, disabled=True, key=f"{key_prefix}_mut_{i}")
                mutations = muts_val
            new_offer.append((crop, weight, mutations))
        return new_offer

    if trade_type == "2 People (Interact)" and trade["joined"]:
        st.markdown("**Your Offer (Editable):**")
        trade["your_offer"] = trade_input_area(trade["your_offer"], editable=True, key_prefix="your")

        st.markdown("**Their Offer (Read-only):**")
        trade["their_offer"] = trade_input_area(trade["their_offer"], editable=False, key_prefix="their")
    else:
        st.markdown("**Your Offer (Read-only):**")
        trade["your_offer"] = trade_input_area(trade["your_offer"], editable=False, key_prefix="your")

        st.markdown("**Their Offer (Read-only):**")
        trade["their_offer"] = trade_input_area(trade["their_offer"], editable=False, key_prefix="their")

    your_total = summarize_trade(trade["your_offer"])
    their_total = summarize_trade(trade["their_offer"])

    st.markdown(f"### Trade Summary:")
    st.write(f"Your Offer Total Value: ₲{your_total:,.2f}")
    st.write(f"Their Offer Total Value: ₲{their_total:,.2f}")
    st.info(fair_trade_result(your_total, their_total))
