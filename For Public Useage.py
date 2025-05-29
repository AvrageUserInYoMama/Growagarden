import streamlit as st
import random

# --------------------------
# Data
# --------------------------
CROP_PRICES = {
    "Carrot": 30, "Strawberry": 90, "Blueberry": 40, "Orange Tulip": 750, "Tomato": 80,
    "Corn": 100, "Daffodil": 60, "Raspberry": 1500, "Pear": 2000, "Pineapple": 3000,
    "Peach": 100, "Apple": 375, "Grape": 10000, "Venus Fly Trap": 15000, "Mango": 6500,
    "Dragon Fruit": 4750, "Cursed Fruit": 50000, "Soul Fruit": 10500, "Candy Blossom": 100000,
    "Lotus": 20000, "Durian": 4500, "Bamboo": 1200, "Coconut": 2500, "Pumpkin": 1000,
    "Watermelon": 1200, "Cactus": 3000, "Passionfruit": 8000, "Pepper": 14000,
    "Starfruit": 7500, "Moonflower": 6000, "Moonglow": 9000, "Blood Banana": 1200,
    "Moon Melon": 15000, "Beanstalk": 18000, "Moon Mango": 36000,
}

PRICE_PER_KG = {
    "Carrot": 100, "Strawberry": 80, "Blueberry": 120, "Orange Tulip": 17000, "Tomato": 60,
    "Corn": 76, "Daffodil": 60, "Raspberry": 60, "Pear": 77, "Pineapple": 750,
    "Peach": 90, "Apple": 77.57, "Grape": 3300, "Venus Fly Trap": 1324, "Mango": 510,
    "Dragon Fruit": 70, "Cursed Fruit": 100, "Soul Fruit": 77, "Candy Blossom": 3900,
    "Lotus": 435, "Durian": 660, "Bamboo": 1051, "Coconut": 50, "Pumpkin": 60,
    "Watermelon": 80, "Cactus": 1110, "Passionfruit": 1400, "Pepper": 1850,
    "Starfruit": 5611, "Moonflower": 4000, "Moonglow": 3400, "Blood Banana": 4600,
    "Moon Melon": 130, "Beanstalk": 2344, "Moon Mango": 2277,
}

MUTATION_MULTIPLIERS = {
    "Wet": 2, "Chilled": 2, "Chocolate": 2, "Moonlit": 2, "Bloodlit": 4,
    "Plasma": 5, "Frozen": 10, "Golden": 20, "Zombified": 25, "Shocked": 50,
    "Rainbow": 50, "Celestial": 120, "Disco": 125, "Twisted": 30,
}

STACKABLE_MUTATIONS = {
    frozenset(["Wet", "Chilled"]): "Frozen",
}

# --------------------------
# Trade Cache (Session Simulated)
# --------------------------
if "trades" not in st.session_state:
    st.session_state.trades = {}

# --------------------------
# UI Layout
# --------------------------
st.title("🌾 Grow a Garden Crop & Trade Calculator")
st.markdown("Calculate crop values, trade offers, and share with friends!")

# --------------------------
# Trading Mode Toggle
# --------------------------
trading_mode = st.checkbox("Enable Trading Mode")

# --------------------------
# Trade Logic
# --------------------------
def calculate_value(item, method, weight, base, mutations):
    # Handle custom price
    price_per_kg = PRICE_PER_KG.get(item, base)
    base_price = CROP_PRICES.get(item, base)

    # Apply stacked mutations
    applied = set(mutations)
    for combo, result in STACKABLE_MUTATIONS.items():
        if combo.issubset(applied):
            applied.difference_update(combo)
            applied.add(result)

    multiplier = sum(MUTATION_MULTIPLIERS.get(m, 0) for m in applied)

    if method == "Weight-based":
        return weight * price_per_kg * (1 + multiplier)
    else:
        return base_price * (1 + multiplier)

# --------------------------
# Trade UI Function
# --------------------------
def trade_ui(label):
    items = []
    for i in range(3):
        col1, col2 = st.columns(2)
        with col1:
            item = st.selectbox(f"{label} Item {i+1}", ["None"] + list(CROP_PRICES.keys()) + ["Custom"], key=f"{label}_item_{i}")
        if item == "None":
            items.append(0)
            continue

        with col2:
            method = st.radio(f"Value type", ["Base Price", "Weight-based"], horizontal=True, key=f"{label}_method_{i}")
            base = st.number_input("Custom Price", min_value=0, value=0, key=f"{label}_base_{i}")
            weight = st.number_input("Weight (kg)", min_value=0.0, value=0.0, key=f"{label}_weight_{i}")
            mutations = st.multiselect("Mutations", MUTATION_MULTIPLIERS.keys(), key=f"{label}_mut_{i}")
            value = calculate_value(item, method, weight, base, mutations)
            items.append(value)
            st.markdown(f"💰 Value: ₵{value:,.2f}")
    return sum(items)

if trading_mode:
    st.subheader("🤝 Trade Comparison")
st.markdown("**We Cant Guarantee Custom Items Are Legitimate**")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Your Offer")
        your_total = trade_ui("your")
    with col2:
        st.markdown("### Their Offer")
        their_total = trade_ui("their")

    st.markdown("### 📊 Trade Verdict")
    st.markdown(f"🧍 You Offer: ₵{your_total:,.2f}")
    st.markdown(f"👤 They Offer: ₵{their_total:,.2f}")
    diff = their_total - your_total
    if abs(diff) < 100:
        verdict = "Fair Trade 🤝"
    elif diff > 0:
        verdict = "You're Winning 🤑"
    else:
        verdict = "You're Losing 😓"
    st.success(verdict)

    st.divider()

    # --------------------------
    # Trade Sharing System
    # --------------------------
    st.subheader("📤 Share Your Offer")

    if st.button("Generate Trade ID"):
        new_id = str(random.randint(10000000, 99999999))
        st.session_state.trades[new_id] = {
            "value": your_total,
            "message": "",
        }
        st.session_state.generated_id = new_id

    if "generated_id" in st.session_state:
        st.markdown(f"🆔 Your Trade ID: `{st.session_state.generated_id}`")
        message = st.text_input("Optional Message", key="message_out")
        st.session_state.trades[st.session_state.generated_id]["message"] = message
        st.success("Copy this ID and give it to the other person!")

    # --------------------------
    # Trade Receiving
    # --------------------------
    st.subheader("📥 Load a Trade")

    trade_id = st.text_input("Enter Trade ID")
    if trade_id and trade_id in st.session_state.trades:
        offer = st.session_state.trades[trade_id]
        st.markdown(f"🧍 Their Offer Value: ₵{offer['value']:,.2f}")
        st.markdown(f"📨 Message: {offer['message']}")

        reply = st.text_input("Reply to Message", key="reply")
        if st.button("Send Reply"):
            st.session_state.trades[trade_id]["reply"] = reply
            st.success("Reply sent!")

        if "reply" in st.session_state.trades[trade_id]:
            st.markdown(f"📩 They Replied: {st.session_state.trades[trade_id]['reply']}")

else:
    # --------------------------
    # Normal Crop Value Calculator
    # --------------------------
    st.subheader("🌱 Crop Value Calculator")

    crop = st.selectbox("Select a Crop", list(CROP_PRICES.keys()) + ["Custom"])
    calc_method = st.radio("Calculation Method", ["Base Price", "Weight-based"])
    base_price = st.number_input("Custom Price (if crop not listed)", min_value=0)
    weight = st.number_input("Enter Weight (kg)", min_value=0.0, format="%.2f")
    selected_mutations = st.multiselect("Select Mutation(s)", list(MUTATION_MULTIPLIERS.keys()))

    value = calculate_value(crop, calc_method, weight, base_price, selected_mutations)
    st.subheader(f"Total Value: ₵{value:,.2f}")

# --------------------------
# Footer
# --------------------------
st.markdown("---")
st.markdown("🔹 **Not Affiliated With _The Garden Game_. Fan-made tool by Gregothey.**")
st.markdown("🔹 **Prices are estimates.**")
