import streamlit as st

# Crop base prices
CROP_PRICES = {
    "Carrot": 20,
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
    "Apple": 400,
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
    "Carrot": 5,
    "Strawberry": 10,
    "Blueberry": 8,
    "Orange Tulip": 15,
    "Tomato": 7,
    "Corn": 6,
    "Daffodil": 4,
    "Raspberry": 12,
    "Pear": 20,
    "Pineapple": 25,
    "Peach": 9,
    "Apple": 3,
    "Grape": 30,
    "Venus Fly Trap": 40,
    "Mango": 22,
    "Dragon Fruit": 18,
    "Cursed Fruit": 100,
    "Soul Fruit": 35,
    "Candy Blossom": 200,
    "Lotus": 50,
    "Durian": 15,
    "Bamboo": 5,
    "Coconut": 10,
    "Pumpkin": 8,
    "Watermelon": 12,
    "Cactus": 20,
    "Passionfruit": 15,
    "Pepper": 10,
    "Starfruit": 25,
    "Moonflower": 20,
    "Moonglow": 30,
    "Blood Banana": 40,
    "Moon Melon": 50,
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
    "Overgrown": 1,
}

# Stackable mutation rules
STACKABLE_MUTATIONS = {
    frozenset(["Wet", "Chilled"]): "Frozen",
}

# Streamlit UI
st.title("Grow a Garden Crop Calculator")

crop = st.selectbox("Select a Crop", list(CROP_PRICES.keys()))
weight = st.number_input("Enter Weight (kg)", min_value=0.0, format="%.2f")
selected_mutations = st.multiselect("Select Mutation(s)", list(MUTATION_MULTIPLIERS.keys()))

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

# Calculate total value based on weight
price_per_kg = PRICE_PER_KG.get(crop, 0)
total_value = weight * price_per_kg * (1 + final_multiplier)  # Total value based on weight and mutations

st.subheader(f"Total Value: ₵{total_value:,.2f}")

# Disclaimers and credits
st.markdown("---")
st.markdown("🔹 **Not Affiliated With _The Garden Game_ or its developers. This is a fan-made tool.**")
st.markdown("🔹 **Prices may vary depending on weight and in-game factors.**")
st.markdown("🔹 **Made by Gregothey.**")
st.markdown("---")
