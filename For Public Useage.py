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
    "Pepper": 5000,
    "Starfruit": 7500,
    "Moonflower": 6000,
    "Moonglow": 9000,
    "Blood Banana": 12000,
    "Moon Melon": 15000,
}

# Price per kilogram for each crop
PRICE_PER_KG = {
    "Carrot": 100,
    "Strawberry": 80,
    "Blueberry": 120,
    "Orange Tulip": 17000,
    "Tomato": 60,
    "Corn": 27,
    "Daffodil": 60,
    "Raspberry": 60,
    "Pear": 20,
    "Pineapple": 750,
    "Peach": 90,
    "Apple": 87,
    "Grape": 3300,
    "Venus Fly Trap": 1324,
    "Mango": 510,
    "Dragon Fruit": 70,
    "Cursed Fruit": 100,
    "Soul Fruit": 35,
    "Candy Blossom": 3900,
    "Lotus": 435,
    "Durian": 660,
    "Bamboo": 1051,
    "Coconut": 29,
    "Pumpkin": 60,
    "Watermelon": 80,
    "Cactus": 1110,
    "Passionfruit": 1400,
    "Pepper": 3811,
    "Starfruit": 5611,
    "Moonflower": 4000,
    "Moonglow": 3400,
    "Blood Banana": 70,
    "Moon Melon": 130,
}

# Mutation multipliers
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

# Stackable mutation rules
STACKABLE_MUTATIONS = {
    frozenset(["Wet", "Chilled"]): "Frozen",
}

# Streamlit UI
st.title("Crop value Calculator")
st.markdown("Know How Valuble A Crop Is Before You Pick It, its  better that way")

crop = st.selectbox("Select a Crop", list(CROP_PRICES.keys()))
weight = st.number_input("Enter Weight (kg)", min_value=0.0, format="%.2f")
selected_mutations = st.multiselect("Select Mutation(s)", list(MUTATION_MULTIPLIERS.keys()))

# Choose calculation method
calculation_method = st.radio("Select Calculation Method", ("Weight-based", "Base Price"))

# Apply stacked mutations (e.g. Wet + Chilled = Frozen)
mutations_to_apply = set(selected_mutations)
for combo, result in STACKABLE_MUTATIONS.items():
    if combo.issubset(mutations_to_apply):
        mutations_to_apply.difference_update(combo)
        mutations_to_apply.add(result)

# Calculate
base_price = CROP_PRICES.get(crop, 0)
final_multiplier = 0  # Initialize to 0 for adding mutation values
for mutation in mutations_to_apply:
    final_multiplier += MUTATION_MULTIPLIERS.get(mutation, 0)  # Add the mutation value

# Calculate total value based on selected method
if calculation_method == "Weight-based":
    price_per_kg = PRICE_PER_KG.get(crop, 0)
    total_value = weight * price_per_kg * (1 + final_multiplier)  # Total value based on weight and mutations
else:  # Base Price Calculation
    total_value = base_price * (1 + final_multiplier)  # Total value based on base price and mutations

st.subheader(f"Total Value: ₵{total_value:,.2f}")

# Disclaimers and credits
st.markdown("---")
st.markdown("🔹 **Not Affiliated With _The Garden Game_ or  the grow a garden developers. This is a fan-made tool.**")
st.markdown("🔹 **These Prices Are A Very Rough Estimate**")
st.markdown("🔹 **Made by Gregothey.**")
st.markdown("---")
