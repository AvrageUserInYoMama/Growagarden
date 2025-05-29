import streamlit as st
import random

st.set_page_config(page_title="Grow A Garden Crop Calculator & Trading", layout="wide")

# Crop & price data
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

STACKABLE_MUTATIONS = {
    frozenset(["Wet", "Chilled"]): "Frozen",
}

def calculate_value(name, base_price, weight, calc_method, mutations):
    # Apply stackable mutations
    mut_set = set(mutations)
    for combo, result in STACKABLE_MUTATIONS.items():
        if combo.issubset(mut_set):
            mut_set.difference_update(combo)
            mut_set.add(result)

    multiplier = sum(MUTATION_MULTIPLIERS.get(m, 0) for m in mut_set)

    if calc_method == "Weight-based":
        return weight * base_price * (1 + multiplier)
    else:
        return base_price * (1 + multiplier)


if "trades" not in st.session_state:
    st.session_state.trades = {}  # trade_code -> trade_data dict
if "messages" not in st.session_state:
    st.session_state.messages = {}  # trade_code -> list of msgs

st.title("🌱 Grow A Garden - Crop Value Calculator & Trading")

mode = st.sidebar.radio("Mode", ["Calculator", "Trading"])

if mode == "Calculator":
    st.header("Crop Value Calculator")

    custom_mode = st.checkbox("Custom Mode (Set your own item & price)", key="calc_custom_mode")

    if custom_mode:
        custom_name = st.text_input("Custom Item Name", key="calc_custom_name")
        custom_price = st.number_input("Custom Base Price (₵)", min_value=0.0, format="%.2f", key="calc_custom_price")
        calc_method = st.radio("Calculation Method", ["Weight-based", "Base Price"], key="calc_custom_method")
        if calc_method == "Weight-based":
            weight = st.number_input("Weight (kg)", min_value=0.0, format="%.2f", key="calc_custom_weight")
        else:
            weight = 1.0
        mutations = st.multiselect("Select Mutation(s)", list(MUTATION_MULTIPLIERS.keys()), key="calc_custom_mutations")

        total_value = calculate_value(custom_name or "Custom Item", custom_price, weight, calc_method, mutations)

    else:
        crop = st.selectbox("Select a Crop", list(CROP_PRICES.keys()), key="calc_crop")
        calc_method = st.radio("Calculation Method", ["Weight-based", "Base Price"], key="calc_method")
        if calc_method == "Weight-based":
            weight = st.number_input("Weight (kg)", min_value=0.0, format="%.2f", key="calc_weight")
        else:
            weight = 1.0
        mutations = st.multiselect("Select Mutation(s)", list(MUTATION_MULTIPLIERS.keys()), key="calc_mutations")

        base_price = CROP_PRICES.get(crop, 0)
        total_value = calculate_value(crop, base_price, weight, calc_method, mutations)

    st.subheader(f"Total Value: ₵{total_value:,.2f}")

elif mode == "Trading":
    st.header("Trading Mode")

    # Trading Mode: Your Offer and Their Offer (3 slots each)

    custom_mode_trade = st.checkbox("Enable Custom Items in Trading Mode", key="trade_custom_mode")

    def render_trade_item(prefix, idx):
        cols = st.columns([3, 2, 3, 3, 4])
        if custom_mode_trade:
            use_custom = cols[0].checkbox("Custom?", key=f"{prefix}_custom_{idx}")
        else:
            use_custom = False

        if use_custom:
            name = cols[0].text_input("Name", key=f"{prefix}_custom_name_{idx}")
            base_price = cols[1].number_input("Base Price (₵)", min_value=0.0, format="%.2f", key=f"{prefix}_custom_price_{idx}")
            calc_method = cols[4].radio("Calc Method", ["Weight-based", "Base Price"], key=f"{prefix}_custom_method_{idx}", horizontal=True)
            if calc_method == "Weight-based":
                weight = cols[2].number_input("Weight (kg)", min_value=0.0, format="%.2f", key=f"{prefix}_custom_weight_{idx}")
            else:
                weight = 1.0
        else:
            name = cols[0].selectbox("Crop", list(CROP_PRICES.keys()), key=f"{prefix}_crop_{idx}")
            base_price = CROP_PRICES.get(name, 0)
            calc_method = cols[4].radio("Calc Method", ["Weight-based", "Base Price"], key=f"{prefix}_method_{idx}", horizontal=True)
            if calc_method == "Weight-based":
                weight = cols[1].number_input("Weight (kg)", min_value=0.0, format="%.2f", key=f"{prefix}_weight_{idx}")
            else:
                weight = 1.0

        mutations = st.multiselect("Mutations", list(MUTATION_MULTIPLIERS.keys()), key=f"{prefix}_mutations_{idx}", help="Select mutations that affect value.")
        value = calculate_value(name or "Item", base_price, weight, calc_method, mutations)
        cols[-2].write(f"Value: ₵{value:,.2f}")
        return value

    st.subheader("Your Offer")
    your_values = [render_trade_item("your", i) for i in range(3)]
    st.subheader("Their Offer")
    their_values = [render_trade_item("their", i) for i in range(3)]

    your_total = sum(your_values)
    their_total = sum(their_values)

    st.markdown(f"**Your Total Offer Value:** ₵{your_total:,.2f}")
    st.markdown(f"**Their Total Offer Value:** ₵{their_total:,.2f}")

    # Fairness check
    diff = their_total - your_total
    if diff > 100:
        fairness = "WIN (You get more value)"
        color = "green"
    elif abs(diff) <= 100:
        fairness = "FAIR TRADE"
        color = "orange"
    else:
        fairness = "LOSS (You get less value)"
        color = "red"

    st.markdown(f"<h3 style='color:{color}'>{fairness}</h3>", unsafe_allow_html=True)

    # Trade code generation modal
    with st.expander("Generate Trade Code"):
        if 'trade_code_modal_open' not in st.session_state:
            st.session_state.trade_code_modal_open = False

        if st.button("Generate Trade Code"):
            st.session_state.trade_code_modal_open = True

        if st.session_state.trade_code_modal_open:
            with st.modal("Enter your Roblox Username to generate trade code"):
                your_username = st.text_input("Your Roblox Username", key="modal_username")
                trade_message = st.text_area("Message to include (optional)", key="modal_message")
                if st.button("Create Trade Code", key="create_trade_code_btn"):
                    if not your_username.strip():
                        st.error("Roblox username is required!")
                    else:
                        # Generate unique 6-digit code
                        while True:
                            code = str(random.randint(100000, 999999))
                            if code not in st.session_state.trades:
                                break
                        # Save trade
                        st.session_state.trades[code] = {
                            "your_total": your_total,
                            "their_total": their_total,
                            "your_username": your_username.strip(),
                            "message": trade_message.strip(),
                            "your_offer": your_values,
                            "their_offer": their_values,
                        }
                        st.session_state.messages[code] = []
                        st.success(f"Trade code generated: **{code}**")
                        st.write(f"Share this code with the other player to join the trade.")
                        st.session_state.trade_code_modal_open = False

    # Join trade
    with st.expander("Join Trade by Code"):
        join_code = st.text_input("Enter Trade Code", key="join_code")
        join_username = st.text_input("Your Roblox Username", key="join_username")
        if st.button("Join Trade"):
            if not join_code.strip() or not join_username.strip():
                st.error("Both trade code and Roblox username are required!")
            elif join_code not in st.session_state.trades:
                st.error("Invalid trade code!")
            else:
                st.session_state.current_trade_code = join_code
                st.session_state.join_username = join_username.strip()
                st.experimental_rerun()

    # Messaging system for joined trade
    if "current_trade_code" in st.session_state and st.session_state.current_trade_code in st.session_state.trades:
        trade_code = st.session_state.current_trade_code
        st.markdown("---")
        st.header(f"Trade Chat for code {trade_code}")

        messages = st.session_state.messages.get(trade_code, [])

        # Display messages
        for msg in messages:
            user = msg.get("user", "Unknown")
            text = msg.get("text", "")
            st.markdown(f"**{user}:** {text}")

        # Send message form
        with st.form("send_message_form"):
            msg_text = st.text_input("Type your message")
            send_btn = st.form_submit_button("Send")
            if send_btn:
                if msg_text.strip():
                    user = st.session_state.get("join_username", "You")
                    st.session_state.messages[trade_code].append({"user": user, "text": msg_text.strip()})
                    st.experimental_rerun()

