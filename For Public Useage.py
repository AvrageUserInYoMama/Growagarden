import streamlit as st

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

# --- UI: Crop Calculator ---
st.title("🌱 Crop Value Calculator")
st.markdown("Know how valuable a crop is before you pick it!")

crop = st.selectbox("Select a Crop", list(CROP_PRICES.keys()))
weight = st.number_input("Enter Weight (kg)", min_value=0.0, format="%.2f")
selected_mutations = st.multiselect("Select Mutation(s)", list(MUTATION_MULTIPLIERS.keys()))
calculation_method = st.radio("Select Calculation Method", ("Weight-based", "Base Price"))

# Apply stacked mutations
mutations_to_apply = set(selected_mutations)
for combo, result in STACKABLE_MUTATIONS.items():
    if combo.issubset(mutations_to_apply):
        mutations_to_apply.difference_update(combo)
        mutations_to_apply.add(result)

# Calculate single crop value
base_price = CROP_PRICES.get(crop, 0)
final_multiplier = sum(MUTATION_MULTIPLIERS.get(m, 0) for m in mutations_to_apply)

if calculation_method == "Weight-based":
    price_per_kg = PRICE_PER_KG.get(crop, 0)
    total_value = weight * price_per_kg * (1 + final_multiplier)
else:
    total_value = base_price * (1 + final_multiplier)

st.subheader(f"Total Value: ₵{total_value:,.2f}")

# --- Trading Mode ---
st.markdown("---")
st.header("💱 Trading Mode")
enable_trading = st.checkbox("Enable Trading Mode")

def get_trade_input(side, index):
    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        crop = st.selectbox(f"{side} Crop {index+1}", ["None"] + list(CROP_PRICES.keys()), key=f"{side}_crop_{index}")
    with col2:
        weight = st.number_input("Weight", min_value=0.0, format="%.2f", key=f"{side}_weight_{index}")
    with col3:
        mutations = st.multiselect("Mutations", list(MUTATION_MULTIPLIERS.keys()), key=f"{side}_mutations_{index}")
    return crop, weight, mutations

def calculate_crop_value(crop, weight, mutations, method):
    if crop == "None":
        return 0
    mutation_set = set(mutations)
    for combo, result in STACKABLE_MUTATIONS.items():
        if combo.issubset(mutation_set):
            mutation_set.difference_update(combo)
            mutation_set.add(result)
    multiplier = sum(MUTATION_MULTIPLIERS.get(m, 0) for m in mutation_set)

    if method == "Weight-based":
        return weight * PRICE_PER_KG.get(crop, 0) * (1 + multiplier)
    else:
        return CROP_PRICES.get(crop, 0) * (1 + multiplier)

if enable_trading:
    trade_method = st.radio("Trade Value Method", ("Weight-based", "Base Price"))

    st.subheader("🧺 Your Offer")
    your_total = 0
    for i in range(3):
        crop, weight, mutations = get_trade_input("Your", i)
        your_total += calculate_crop_value(crop, weight, mutations, trade_method)

    st.subheader("🎁 Their Offer")
    their_total = 0
    for i in range(3):
        crop, weight, mutations = get_trade_input("Their", i)
        their_total += calculate_crop_value(crop, weight, mutations, trade_method)

    st.markdown(f"**Your Total Value:** ₵{your_total:,.2f}")
    st.markdown(f"**Their Total Value:** ₵{their_total:,.2f}")

    # Determine trade fairness
    if your_total == 0 and their_total == 0:
        result = "🧐 No trade inputs yet."
    elif their_total > your_total * 1.15:
        result = "✅ You're Winning!"
    elif your_total > their_total * 1.15:
        result = "❌ You're Losing!"
    else:
        result = "⚖️ Fair Trade"

    st.subheader(f"**Trade Verdict:** {result}")

# --- Footer ---
st.markdown("---")
st.markdown("🔹 **Not Affiliated With _The Garden Game_ or Grow a Garden devs.**")
st.markdown("🔹 **Prices are rough estimates.**")
st.markdown("🔹 **Made by Gregothey.**")
