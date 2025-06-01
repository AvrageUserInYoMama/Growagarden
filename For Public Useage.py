import streamlit as st

# ✅ MUST BE FIRST
st.set_page_config(page_title="Grow a Garden App", layout="wide")

# Now import or define everything else
# === Crop Values ===
BASE_PRICES = {
    "Carrot": 22,
    "Strawberry": 19,
    "Blueberry": 21,
    "Orange Tulip": 792,
    "Tomato": 35,
    "Corn": 44,
    "Daffodil": 988,
    "Watermelon": 2905,
    "Pumpkin": 3854,
    "Apple": 266,
    "Bamboo": 3944,
    "Coconut": 2670,
    "Cactus": 3224,
    "Dragon Fruit": 4566,
    "Mango": 6308,
    "Grape": 7554,
    "Mushroom": 142443,
    "Pepper": 7577,
    "Cacao": 10456,
    "Beanstalk": 18788,
    "Peach": 283,
    "Pineapple": 2350,
    "Moonglow": 20300,
    "Blood Banana": 6100,
    "Moon Melon": 17750,
    "Celestiberry": 9100,
    "Moonflower": 8900,
    "Starfruit": 14559, # Using the second value listed for Starfruit from PCGamesN
    "Mint": 6800,
    "Nightshade": 2300,
    "Raspberry": 98,
    "Pear": 553,
    "Glowshroom": 282,
    "Moon Mango": 24340,
    "Moon Blossom": 53512,
    "Soul Fruit": 3328,
    "Cursed Fruit": 15944,
    "Lotus": 24598,
    "Candy Blossom": 99436,
    "Cherry Blossom": 566,
    "Venus Fly Trap": 18854,
    "Banana": 1634,
    "Lemon": 554,
    "Passionfruit": 3299,
    "Eggplant": 7089,
    "Cranberry": 2054,
    "Durian": 4911,
    "Easter Egg": 4844,
    "Papaya": 1288,
    "Candy Sunflower": 164440,
    "Red Lollipop": 81297,
    "Chocolate Carrot": 17258,
    "Hive Fruit": 1038,
    "Sunflower": 6318,
    "Pink Lily": 58663,
    "Nectarine": 35000,
    "Purple Dahlia": 65000,
    "Lilac": 940000,            
    "Rose": 4513,
    "Foxglove": 15500  
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
    "Moon Mango": 5544,
}

MUTATION_MULTIPLIERS = {
    "Pollinated": 2, "Wet": 2, "Chilled": 2, "Chocolate": 2, "Moonlit": 2,
    "Bloodlit": 4, "Plasma": 5, "Frozen": 10, "Golden": 20, "Zombified": 25,
    "Shocked": 50, "Rainbow": 50, "Celestial": 120, "Disco": 125, "Twisted": 30,
    "Pollinated": 32, "Voided": 155,
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

