import streamlit as st
import random

# Data
CROP_PRICES = {
    "Carrot": 30, "Strawberry": 90, "Blueberry": 40, "Orange Tulip": 750,
    "Tomato": 80, "Corn": 100, "Daffodil": 60, "Raspberry": 1500,
    "Pear": 2000, "Pineapple": 3000, "Peach": 100, "Apple": 375,
    "Grape": 10000, "Venus Fly Trap": 15000, "Mango": 6500, "Dragon Fruit": 4750,
    "Cursed Fruit": 50000, "Soul Fruit": 10500, "Candy Blossom": 100000,
    "Lotus": 20000, "Durian": 4500, "Bamboo": 1200, "Coconut": 2500,
    "Pumpkin": 1000, "Watermelon": 1200, "Cactus": 3000, "Passionfruit": 8000,
    "Pepper": 14000, "Starfruit": 7500, "Moonflower": 6000, "Moonglow": 9000,
    "Blood Banana": 1200, "Moon Melon": 15000, "Beanstalk": 18000, "Moon Mango": 36000,
}

PRICE_PER_KG = {
    "Carrot": 100, "Strawberry": 80, "Blueberry": 120, "Orange Tulip": 17000,
    "Tomato": 60, "Corn": 76, "Daffodil": 60, "Raspberry": 60,
    "Pear": 77, "Pineapple": 750, "Peach": 90, "Apple": 77.57,
    "Grape": 3300, "Venus Fly Trap": 1324, "Mango": 510, "Dragon Fruit": 70,
    "Cursed Fruit": 100, "Soul Fruit": 77, "Candy Blossom": 3900,
    "Lotus": 435, "Durian": 660, "Bamboo": 1051, "Coconut": 50,
    "Pumpkin": 60, "Watermelon": 80, "Cactus": 1110, "Passionfruit": 1400,
    "Pepper": 1850, "Starfruit": 5611, "Moonflower": 4000, "Moonglow": 3400,
    "Blood Banana": 4600, "Moon Melon": 130, "Beanstalk": 2344, "Moon Mango": 2277,
}

MUTATION_MULTIPLIERS = {
    "Wet": 2, "Chilled": 2, "Chocolate": 2, "Moonlit": 2,
    "Bloodlit": 4, "Plasma": 5, "Frozen": 10, "Golden": 20,
    "Zombified": 25, "Shocked": 50, "Rainbow": 50,
    "Celestial": 120, "Disco": 125, "Twisted": 30,
}

STACKABLE_MUTATIONS = {
    frozenset(["Wet", "Chilled"]): "Frozen",
}

# Helper functions
def apply_stackable_mutations(selected_mutations):
    mutations = set(selected_mutations)
    for combo, result in STACKABLE_MUTATIONS.items():
        if combo.issubset(mutations):
            mutations.difference_update(combo)
            mutations.add(result)
    return list(mutations)

def calculate_value(name, base_price, weight, method, mutations):
    mutations = apply_stackable_mutations(mutations)
    multiplier = sum(MUTATION_MULTIPLIERS.get(m, 0) for m in mutations)
    if method == "Weight-based":
        price_per_kg = PRICE_PER_KG.get(name, base_price)
        total = weight * price_per_kg * (1 + multiplier)
    else:
        total = base_price * (1 + multiplier)
    return total

# Session states for trading messages & trades
if 'trades' not in st.session_state:
    st.session_state.trades = {}

if 'messages' not in st.session_state:
    st.session_state.messages = {}

# UI Starts
st.title("Grow a Garden Crop & Trading Calculator")

trading_mode = st.checkbox("Enable Trading Mode")

if not trading_mode:
    # --- Single Calc Mode ---
    custom_mode = st.checkbox("Custom Mode (Set your own item & price)", key="custom_mode_main")

    if custom_mode:
        custom_name = st.text_input("Custom Item Name", key="custom_name_main")
        custom_price = st.number_input("Custom Base Price (₵)", min_value=0.0, format="%.2f", key="custom_price_main")
        calculation_method = st.radio("Calculation Method", ["Weight-based", "Base Price"], key="custom_method_main")

        if calculation_method == "Weight-based":
            weight = st.number_input("Weight (kg)", min_value=0.0, format="%.2f", key="custom_weight_main")
        else:
            weight = 1.0  # dummy for base price calc

        mutations = st.multiselect("Select Mutation(s)", list(MUTATION_MULTIPLIERS.keys()), key="custom_mutations_main")

        total_value = calculate_value(custom_name or "Custom Item", custom_price, weight, calculation_method, mutations)

    else:
        crop = st.selectbox("Select a Crop", list(CROP_PRICES.keys()))
        calculation_method = st.radio("Calculation Method", ["Weight-based", "Base Price"], key="calc_method_main")

        if calculation_method == "Weight-based":
            weight = st.number_input("Weight (kg)", min_value=0.0, format="%.2f", key="weight_main")
        else:
            weight = 1.0  # dummy for base price calc

        mutations = st.multiselect("Select Mutation(s)", list(MUTATION_MULTIPLIERS.keys()), key="mutations_main")

        total_value = calculate_value(crop, CROP_PRICES.get(crop, 0), weight, calculation_method, mutations)

    st.subheader(f"Total Value: ₵{total_value:,.2f}")

else:
    # --- Trading Mode ---
    st.header("Trading Mode")
    custom_mode_trade = st.checkbox("Enable Custom Items in Trading", key="custom_mode_trade")

    def render_item(prefix, idx):
        cols = st.columns([2, 2, 2, 3])
        use_custom = False
        if custom_mode_trade:
            use_custom = cols[0].checkbox("Custom?", key=f"{prefix}_custom_{idx}")

        if use_custom:
            name = cols[0].text_input("Name", key=f"{prefix}_custom_name_{idx}")
            base_price = cols[1].number_input("Base Price (₵)", min_value=0.0, format="%.2f", key=f"{prefix}_custom_price_{idx}")
            weight = cols[2].number_input("Weight (kg)", min_value=0.0, format="%.2f", key=f"{prefix}_custom_weight_{idx}")
            method = cols[3].radio("Calc Method", ["Weight-based", "Base Price"], key=f"{prefix}_custom_method_{idx}", horizontal=True)
        else:
            name = cols[0].selectbox("Crop", list(CROP_PRICES.keys()), key=f"{prefix}_crop_{idx}")
            base_price = CROP_PRICES.get(name, 0)
            weight = cols[1].number_input("Weight (kg)", min_value=0.0, format="%.2f", key=f"{prefix}_weight_{idx}")
            method = "Weight-based"
            cols[3].write("")  # empty space

        mutations = st.multiselect(f"Mutations - {prefix} item {idx+1}", list(MUTATION_MULTIPLIERS.keys()), key=f"{prefix}_mutations_{idx}")

        value = calculate_value(name, base_price, weight, method, mutations)
        st.write(f"Value: ₵{value:,.2f}")
        return value

    st.subheader("Your Offer")
    your_total = sum(render_item("your", i) for i in range(3))

    st.subheader("Their Offer")
    their_total = sum(render_item("their", i) for i in range(3))

    st.markdown("---")
    st.subheader("Trade Summary")
    st.write(f"Your offer total: ₵{your_total:,.2f}  |  Their offer total: ₵{their_total:,.2f}")

    diff = their_total - your_total
    if diff > 50:
        st.success("Win! Their offer is worth more than yours.")
    elif abs(diff) <= 50:
        st.info("Fair trade! Offers are close in value.")
    else:
        st.error("Loss! Your offer is worth more than theirs.")

    # --- Trade Code and Messaging ---
    st.markdown("---")
    st.subheader("Trade Code & Messaging")

    action = st.radio("Action:", ["Generate Trade Code", "Join Trade by Code"], index=0)

    if action == "Generate Trade Code":
        your_username = st.text_input("Your Roblox Username")
        their_username = st.text_input("Their Roblox Username")
        trade_message = st.text_area("Message to include (optional)")
        if st.button("Generate Trade Code"):
            if not your_username or not their_username:
                st.error("Both usernames are required!")
            else:
                # Generate random 5-digit code (unique)
                while True:
                    code = str(random.randint(10000, 99999))
                    if code not in st.session_state.trades:
                        break
                # Store trade details
                st.session_state.trades[code] = {
                    "your_total": your_total,
                    "their_total": their_total,
                    "your_username": your_username,
                    "their_username": their_username,
                    "message": trade_message,
                }
                st.session_state.messages[code] = []
                st.success(f"Trade code generated: **{code}**")
                st.write(f"Share this code with {their_username} to join the trade.")

    else:  # Join Trade
        trade_code = st.text_input("Enter Trade Code")
        join_username = st.text_input("Your Roblox Username")

        if st.button("Join Trade"):
            if not trade_code or not join_username:
                st.error("Trade code and username are required!")
            elif trade_code not in st.session_state.trades:
                st.error("Invalid trade code!")
            else:
                st.success(f"Joined trade {trade_code} as {join_username}.")

                # Show trade details & messaging
                trade = st.session_state.trades[trade_code]
                st.markdown("### Trade Details")
                st.write(f"Your offer total: ₵{trade['your_total']:,.2f}")
                st.write(f"Their offer total: ₵{trade['their_total']:,.2f}")
                st.write(f"Trade between: {trade['your_username']} and {trade['their_username']}")
                if trade["message"]:
                    st.info(f"Message from initiator: {trade['message']}")

                # Messaging chat
                chat_col1, chat_col2 = st.columns([4,1])
                with chat_col1:
                    messages = st.session_state.messages.get(trade_code, [])
                    st.markdown("### Messages")
                    for msg in messages:
                        st.write(f"**{msg['user']}:** {msg['text']}")
                    new_msg = st.text_input("Send message", key=f"msg_input_{trade_code}")
                with chat_col2:
                    if st.button("Send", key=f"msg_send_{trade_code}"):
                        if new_msg.strip():
                            messages.append({"user": join_username, "text": new_msg.strip()})
                            st.session_state.messages[trade_code] = messages
                            st.experimental_rerun()

st.markdown("---")
st.markdown("🔹 **Not affiliated with _The Garden Game_ or the Grow a Garden developers. This is a fan-made tool.**")
st.markdown("🔹 **Prices are rough estimates.**")
st.markdown("🔹 **Made by Gregothey.**")


