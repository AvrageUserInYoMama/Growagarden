import streamlit as st
import random
from datetime import datetime

# --- Data dictionaries ---

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

STACKABLE_MUTATIONS = {
    frozenset(["Wet", "Chilled"]): "Frozen",
}

# --- Initialize session state variables ---
if "trade_codes" not in st.session_state:
    st.session_state.trade_codes = {}  # trade_code -> trade_data dict

if "messages" not in st.session_state:
    st.session_state.messages = {}  # trade_code -> list of (username, message)

if "joined_trade" not in st.session_state:
    st.session_state.joined_trade = None  # current trade code user joined

if "username" not in st.session_state:
    st.session_state.username = ""

# --- Helper functions ---

def calculate_value(name, base_price, weight, method, mutations):
    """Calculate total value with mutations"""
    # Apply stacked mutations
    mutations_to_apply = set(mutations)
    for combo, result in STACKABLE_MUTATIONS.items():
        if combo.issubset(mutations_to_apply):
            mutations_to_apply.difference_update(combo)
            mutations_to_apply.add(result)
    # Sum multipliers
    final_multiplier = sum(MUTATION_MULTIPLIERS.get(m, 0) for m in mutations_to_apply)
    if method == "Weight-based":
        price_per_kg = PRICE_PER_KG.get(name, base_price)
        return weight * price_per_kg * (1 + final_multiplier)
    else:  # Base price method
        return base_price * (1 + final_multiplier)

def evaluate_trade(offer1, offer2):
    """Compare total value of two offers and return status"""
    v1 = sum(item['value'] for item in offer1)
    v2 = sum(item['value'] for item in offer2)
    diff = v2 - v1
    if diff > v1 * 0.1:
        return "WIN"
    elif abs(diff) <= v1 * 0.1:
        return "FAIR"
    else:
        return "LOSS"

def generate_trade_code():
    return str(random.randint(100000, 999999999))

# --- UI Starts ---

st.title("Grow a Garden Crop Value & Trading Calculator")
st.markdown("Know how valuable a crop or item is before trading or picking it!")

trade_mode = st.checkbox("Trading Mode")

if not trade_mode:
    # Crop calculator mode
    crop = st.selectbox("Select a Crop", list(CROP_PRICES.keys()))
    weight = st.number_input("Enter Weight (kg)", min_value=0.0, format="%.2f")
    custom_base_price = st.number_input("Or Enter Base Price (₵)", min_value=0.0, format="%.2f", value=0.0)
    selected_mutations = st.multiselect("Select Mutation(s)", list(MUTATION_MULTIPLIERS.keys()))

    calc_method = st.radio("Select Calculation Method", ["Weight-based", "Base Price"])

    base_price_used = CROP_PRICES.get(crop, 0) if custom_base_price == 0 else custom_base_price

    total_value = calculate_value(
        crop, base_price_used, weight, calc_method, selected_mutations
    )

    st.subheader(f"Total Value: ₵{total_value:,.2f}")

else:
    st.subheader("Trading Mode")

    # Trading state - choose to generate or join
    option = st.radio("Do you want to generate a trade offer or join one?", ("Generate Offer", "Join Trade"))

    if option == "Generate Offer":
        username_input = st.text_input("Enter your Roblox Username (required to generate trade code)")
        if not username_input.strip():
            st.warning("Please enter your Roblox username.")
        else:
            st.session_state.username = username_input.strip()

            # Your Offer Input
            st.markdown("### Your Offer")
            your_offer = []
            for i in range(3):
                st.markdown(f"**Your Item {i+1}**")
                name = st.text_input(f"Item Name (custom allowed) - Your item {i+1}", key=f"your_name_{i}")
                use_base = st.checkbox(f"Use Base Price for '{name}'", key=f"your_baseprice_chk_{i}")
                if use_base:
                    price = st.number_input(f"Base Price (₵) for '{name}'", min_value=0.0, key=f"your_price_{i}")
                    weight_i = 0
                else:
                    weight_i = st.number_input(f"Weight (kg) for '{name}'", min_value=0.0, format="%.2f", key=f"your_weight_{i}")
                    price = CROP_PRICES.get(name, 0)
                your_offer.append({"name": name, "base_price": price, "weight": weight_i, "mutations": [], "use_base": use_base})

            # Their Offer Input
            st.markdown("### Their Offer")
            their_offer = []
            for i in range(3):
                st.markdown(f"**Their Item {i+1}**")
                name = st.text_input(f"Item Name (custom allowed) - Their item {i+1}", key=f"their_name_{i}")
                use_base = st.checkbox(f"Use Base Price for '{name}'", key=f"their_baseprice_chk_{i}")
                if use_base:
                    price = st.number_input(f"Base Price (₵) for '{name}'", min_value=0.0, key=f"their_price_{i}")
                    weight_i = 0
                else:
                    weight_i = st.number_input(f"Weight (kg) for '{name}'", min_value=0.0, format="%.2f", key=f"their_weight_{i}")
                    price = CROP_PRICES.get(name, 0)
                their_offer.append({"name": name, "base_price": price, "weight": weight_i, "mutations": [], "use_base": use_base})

            if st.button("Generate Trade Code"):
                # Calculate values for your offer
                for item in your_offer:
                    item['value'] = calculate_value(item['name'], item['base_price'], item['weight'], "Base Price" if item['use_base'] else "Weight-based", item['mutations'])
                # Calculate values for their offer
                for item in their_offer:
                    item['value'] = calculate_value(item['name'], item['base_price'], item['weight'], "Base Price" if item['use_base'] else "Weight-based", item['mutations'])

                trade_code = generate_trade_code()

                # Store trade info
                st.session_state.trade_codes[trade_code] = {
                    "creator": st.session_state.username,
                    "your_offer": your_offer,
                    "their_offer": their_offer,
                    "created_at": datetime.now().isoformat(),
                }
                st.session_state.messages[trade_code] = []

                st.session_state.joined_trade = trade_code
                st.success(f"Trade code generated: **{trade_code}**. Share this code with your trading partner!")
                st.experimental_rerun()

    elif option == "Join Trade":
        trade_code_input = st.text_input("Enter Trade Code")
        if trade_code_input and trade_code_input.strip() in st.session_state.trade_codes:
            username_input = st.text_input("Enter your Roblox Username (required to join trade)")
            if not username_input.strip():
                st.warning("Please enter your Roblox username.")
            else:
                st.session_state.username = username_input.strip()
                trade_code = trade_code_input.strip()
                st.session_state.joined_trade = trade_code
                st.experimental_rerun()
        elif trade_code_input:
            st.error("Invalid Trade Code!")

    # If joined to a trade
    if st.session_state.joined_trade:
        trade_code = st.session_state.joined_trade
        trade_data = st.session_state.trade_codes.get(trade_code, None)
        if not trade_data:
            st.error("Trade data not found. Please generate or join a valid trade.")
            st.session_state.joined_trade = None
        else:
            st.markdown(f"### Trade Code: {trade_code}")
            st.markdown(f"**Created by:** {trade_data['creator']}")

            # Show offers and their total values
            your_offer = trade_data['your_offer']
            their_offer = trade_data['their_offer']

            your_total = sum(item['value'] for item in your_offer)
            their_total = sum(item['value'] for item in their_offer)

            st.markdown("#### Your Offer")
            for item in your_offer:
                st.markdown(f"- {item['name']} - ₵{item['value']:,.2f}")

            st.markdown(f"**Total Value: ₵{your_total:,.2f}**")

            st.markdown("#### Their Offer")
            for item in their_offer:
                st.markdown(f"- {item['name']} - ₵{item['value']:,.2f}")

            st.markdown(f"**Total Value: ₵{their_total:,.2f}**")

            trade_result = evaluate_trade(your_offer, their_offer)
            st.markdown(f"### Trade Evaluation: **{trade_result}**")

            # Chat system
            st.markdown("---")
            st.markdown("### Trade Chat")

            if trade_code not in st.session_state.messages:
                st.session_state.messages[trade_code] = []

            for username_msg, msg in st.session_state.messages[trade_code]:
                st.write(f"**{username_msg}:** {msg}")

            new_message = st.text_input("Type your message")
            if st.button("Send Message"):
                if new_message.strip():
                    st.session_state.messages[trade_code].append((st.session_state.username, new_message.strip()))
                    st.experimental_rerun()

            if st.button("Leave Trade"):
                st.session_state.joined_trade = None
                st.experimental_rerun()

# --- Footer ---
st.markdown("---")
st.markdown("🔹 **Not Affiliated With _The Garden Game_ or Grow a Garden developers. This is a fan-made tool.**")
st.markdown("🔹 **Prices are rough estimates. Use at your own discretion.**")
st.markdown("🔹 **Made by Gregothey.**")
