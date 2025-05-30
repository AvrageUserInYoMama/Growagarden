import streamlit as st

# ✅ MUST BE FIRST
st.set_page_config(page_title="Grow a Garden App", layout="wide")

# Now import or define everything else
# === Crop Values ===
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


# === Constants ===
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
    "Pollinated": 2, "Wet": 2, "Chilled": 2, "Chocolate": 2, "Moonlit": 2,
    "Bloodlit": 4, "Plasma": 5, "Frozen": 10, "Golden": 20, "Zombified": 25,
    "Shocked": 50, "Rainbow": 50, "Celestial": 120, "Disco": 125, "Twisted": 30,
}

# === Helper ===
def calculate_value(crop, weight, mutations):
    base = PRICE_PER_KG.get(crop, 0)
    multiplier = 1
    for m in mutations:
        multiplier *= MUTATION_MULTIPLIERS.get(m, 1)
    return base * weight * multiplier

# === UI ===
st.title("🌿 Grow a Garden - Calculator & Trading App")

tabs = st.tabs(["📈 Calculator", "🔁 Trading", "📚 Values"])

# === Calculator Tab ===
with tabs[0]:
    st.header("📈 Value Calculator")
    crop = st.selectbox("Select crop", BASE_PRICES.keys())
    weight = st.number_input("Enter weight (kg)", 0.1, 10000.0, step=0.1)
    mutations = st.multiselect("Mutations (multi-select)", MUTATION_MULTIPLIERS.keys())

    if st.button("Calculate Value"):
        value = calculate_value(crop, weight, mutations)
        st.success(f"Total Value: {value:.2f} coins")

# === Trading Tab ===
with tabs[1]:
    st.header("🔁 Trade Comparison")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Trader A")
        crop_a = st.selectbox("Crop A", BASE_PRICES.keys(), key="a")
        weight_a = st.number_input("Weight A (kg)", 0.1, 10000.0, step=0.1, key="wa")
        muts_a = st.multiselect("Mutations A", MUTATION_MULTIPLIERS.keys(), key="ma")

    with col2:
        st.subheader("Trader B")
        crop_b = st.selectbox("Crop B", BASE_PRICES.keys(), key="b")
        weight_b = st.number_input("Weight B (kg)", 0.1, 10000.0, step=0.1, key="wb")
        muts_b = st.multiselect("Mutations B", MUTATION_MULTIPLIERS.keys(), key="mb")

    if st.button("Compare Trade"):
        val_a = calculate_value(crop_a, weight_a, muts_a)
        val_b = calculate_value(crop_b, weight_b, muts_b)

        st.write(f"💰 Trader A: `{val_a:.2f}` coins")
        st.write(f"💰 Trader B: `{val_b:.2f}` coins")

        diff = abs(val_a - val_b)
        threshold = max(val_a, val_b) * 0.1

        if diff <= threshold:
            st.success("✅ Fair trade!")
        else:
            st.error("❌ Unfair trade!")

# === Values Tab ===
with tabs[2]:
    st.header("📚 Crop Values")
    st.subheader("Base Prices / Price per KG")
    st.dataframe(
        [{"Crop": k, "Base Price": BASE_PRICES[k], "Price per KG": PRICE_PER_KG[k]}
         for k in BASE_PRICES]
    )

    st.subheader("🌟 Mutations & Multipliers")
    st.dataframe(
        [{"Mutation": k, "Multiplier": v} for k, v in MUTATION_MULTIPLIERS.items()]
    )


    st.caption("Grow a Garden Fan Tool, By Gregothey.")
    st.caption("Prices Are A Rough Estmite Will Not Be Spot On!")

