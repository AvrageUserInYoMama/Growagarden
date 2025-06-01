import streamlit as st

# ✅ MUST BE FIRST
st.set_page_config(page_title="Grow a Garden App", layout="wide")

# Now import or define everything else
# === Crop Values ===
BASE_PRICES = {
    "Carrot": 22, "Strawberry": 19, "Blueberry": 21, "Orange Tulip": 792,
    "Tomato": 35, "Corn": 44, "Daffodil": 988, "Watermelon": 2905,
    "Pumpkin": 3854, "Apple": 266, "Bamboo": 3944, "Coconut": 2670,
    "Cactus": 3224, "Dragon Fruit": 4566, "Mango": 6308, "Grape": 7554,
    "Mushroom": 142443, "Pepper": 7577, "Cacao": 10456, "Beanstalk": 18788,
    "Peach": 283, "Pineapple": 2350, "Moonglow": 20300, "Blood Banana": 6100,
    "Moon Melon": 17750, "Celestiberry": 9100, "Moonflower": 8900,
    "Starfruit": 14559, "Mint": 6800, "Nightshade": 2300, "Raspberry": 98,
    "Pear": 553, "Glowshroom": 282, "Moon Mango": 24340, "Moon Blossom": 53512,
    "Soul Fruit": 3328, "Cursed Fruit": 15944, "Lotus": 24598,
    "Candy Blossom": 99436, "Cherry Blossom": 566, "Venus Fly Trap": 18854,
    "Banana": 1634, "Lemon": 554, "Passionfruit": 3299, "Eggplant": 7089,
    "Cranberry": 2054, "Durian": 4911, "Easter Egg": 4844, "Papaya": 1288,
    "Candy Sunflower": 164440, "Red Lollipop": 81297, "Chocolate Carrot": 17258,
    "Hive Fruit": 1038, "Sunflower": 6318, "Pink Lily": 58663,
    "Nectarine": 35000, "Purple Dahlia": 65000, "Lilac": 940000,
    "Rose": 4513, "Foxglove": 15500
}

# === Constants ===
PRICE_PER_KG = {
    "Carrot": 100, "Strawberry": 80, "Blueberry": 120, "Orange Tulip": 17000,
    "Tomato": 60, "Corn": 76, "Daffodil": 60, "Raspberry": 60, "Pear": 77,
    "Pineapple": 750, "Peach": 90, "Apple": 77.57, "Grape": 3300,
    "Venus Fly Trap": 1324, "Mango": 510, "Dragon Fruit": 70,
    "Cursed Fruit": 100, "Soul Fruit": 77, "Candy Blossom": 3900, "Lotus": 435,
    "Durian": 660, "Bamboo": 1051, "Coconut": 50, "Pumpkin": 60,
    "Watermelon": 80, "Cactus": 1110, "Passionfruit": 1400, "Pepper": 1850,
    "Starfruit": 5611, "Moonflower": 4000, "Moonglow": 3400,
    "Blood Banana": 4600, "Moon Melon": 130, "Beanstalk": 2344,
    "Moon Mango": 5544, "Mushroom": 0, "Cacao": 0, "Celestiberry": 0,
    "Mint": 0, "Nightshade": 0, "Glowshroom": 0, "Moon Blossom": 0,
    "Cherry Blossom": 0, "Banana": 0, "Lemon": 0, "Eggplant": 0,
    "Cranberry": 0, "Easter Egg": 0, "Papaya": 0, "Candy Sunflower": 0,
    "Red Lollipop": 0, "Chocolate Carrot": 0, "Hive Fruit": 0, "Sunflower": 0,
    "Pink Lily": 0, "Nectarine": 0, "Purple Dahlia": 0, "Lilac": 0, "Rose": 0,
    "Foxglove": 0
}

MUTATION_MULTIPLIERS = {
    "Wet": 2, "Chilled": 2, "Chocolate": 2, "Moonlit": 2, # Note: Pollinated appears twice, using the first one.
    "Bloodlit": 4, "Plasma": 5, "Frozen": 10, "Golden": 20, "Zombified": 25,
    "Shocked": 50, "Rainbow": 50, "Celestial": 120, "Disco": 125, "Twisted": 30,
    "Pollinated": 32, # This was a duplicate, a choice needs to be made or keys differentiated. Using first one.
    "Voided": 155,
}



# === Helper ===
def calculate_value(crop, units, mutations, calculation_mode):
    initial_value = 0
    if calculation_mode == "Price per KG":
        base_unit_price = PRICE_PER_KG.get(crop, 0)
        initial_value = base_unit_price * units  # units is weight
    elif calculation_mode == "Fixed Base Price per Item":
        base_item_price = BASE_PRICES.get(crop, 0)
        initial_value = base_item_price * units  # units is quantity
    else:
        st.error("Invalid calculation mode selected.")
        return 0

    mutation_multiplier_total = 1
    for m in mutations:
        mutation_multiplier_total *= MUTATION_MULTIPLIERS.get(m, 1)

    return initial_value * mutation_multiplier_total

# === UI ===
st.title("🌿 Grow a Garden - Calculator & Trading App")

tabs = st.tabs(["📈 Calculator", "🔁 Trading", "📚 Values"])

# === Calculator Tab ===
with tabs[0]:
    st.header("📈 Value Calculator")
    crop_calc = st.selectbox("Select crop", BASE_PRICES.keys(), key="crop_calc")

    calc_mode = st.radio(
        "Select Calculation Mode:",
        ("Price per KG", "Fixed Base Price per Item"),
        key="calc_mode_main"
    )

    units_label = "Enter weight (kg)"
    units_min_value = 0.1
    units_step = 0.1
    units_format = "%.1f"
    units_default = 1.0

    if calc_mode == "Fixed Base Price per Item":
        units_label = "Enter quantity (items)"
        units_min_value = 1.0
        units_step = 1.0
        units_format = "%d" # Format as integer
        units_default = 1.0


    units_calc = st.number_input(
        units_label,
        min_value=units_min_value,
        value=units_default,
        step=units_step,
        format=units_format,
        key="units_calc"
    )
    mutations_calc = st.multiselect(
        "Mutations (multi-select)",
        MUTATION_MULTIPLIERS.keys(),
        key="mutations_calc"
    )

    if st.button("Calculate Value", key="btn_calc"):
        value = calculate_value(crop_calc, units_calc, mutations_calc, calc_mode)
        st.success(f"Total Value: {value:,.2f} coins")

# === Trading Tab ===
with tabs[1]:
    st.header("🔁 Trade Comparison")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Trader A")
        crop_a = st.selectbox("Crop A", BASE_PRICES.keys(), key="crop_a")
        mode_a = st.radio(
            "Calculation Mode A:",
            ("Price per KG", "Fixed Base Price per Item"),
            key="mode_a"
        )
        units_label_a = "Weight A (kg)"
        units_min_a = 0.1
        units_step_a = 0.1
        units_format_a = "%.1f"
        units_default_a = 1.0
        if mode_a == "Fixed Base Price per Item":
            units_label_a = "Quantity A (items)"
            units_min_a = 1.0
            units_step_a = 1.0
            units_format_a = "%d"

        units_a = st.number_input(units_label_a, min_value=units_min_a, value=units_default_a, step=units_step_a, format=units_format_a, key="units_a")
        muts_a = st.multiselect("Mutations A", MUTATION_MULTIPLIERS.keys(), key="ma")

    with col2:
        st.subheader("Trader B")
        crop_b = st.selectbox("Crop B", BASE_PRICES.keys(), key="crop_b")
        mode_b = st.radio(
            "Calculation Mode B:",
            ("Price per KG", "Fixed Base Price per Item"),
            key="mode_b"
        )
        units_label_b = "Weight B (kg)"
        units_min_b = 0.1
        units_step_b = 0.1
        units_format_b = "%.1f"
        units_default_b = 1.0
        if mode_b == "Fixed Base Price per Item":
            units_label_b = "Quantity B (items)"
            units_min_b = 1.0
            units_step_b = 1.0
            units_format_b = "%d"

        units_b = st.number_input(units_label_b, min_value=units_min_b, value=units_default_b, step=units_step_b, format=units_format_b, key="units_b")
        muts_b = st.multiselect("Mutations B", MUTATION_MULTIPLIERS.keys(), key="mb")

    if st.button("Compare Trade", key="btn_compare"):
        val_a = calculate_value(crop_a, units_a, muts_a, mode_a)
        val_b = calculate_value(crop_b, units_b, muts_b, mode_b)

        st.write(f"💰 Trader A Value: `{val_a:,.2f}` coins")
        st.write(f"💰 Trader B Value: `{val_b:,.2f}` coins")

        diff = abs(val_a - val_b)
        # Consider a threshold for fairness, e.g., 10% of the higher value
        threshold = max(val_a, val_b) * 0.1 if max(val_a, val_b) > 0 else 0 # Avoid division by zero if both are 0

        if val_a == val_b: # Perfect match
             st.success("✅ Perfectly fair trade!")
        elif diff <= threshold:
            st.success("✅ Seems like a fair trade!")
        else:
            st.error("⚖️ Potentially unfair trade! Review values.")
            if val_a > val_b:
                st.write(f"Trader A's offer is worth {diff:,.2f} coins more.")
            else:
                st.write(f"Trader B's offer is worth {diff:,.2f} coins more.")


# === Values Tab ===
with tabs[2]:
    st.header("📚 Crop Values Reference")
    st.subheader("Defined Prices")
    st.dataframe(
        [{"Crop": k, "Base Price (per item)": BASE_PRICES.get(k, "N/A"), "Price per KG": PRICE_PER_KG.get(k, "N/A")}
         for k in sorted(list(set(list(BASE_PRICES.keys()) + list(PRICE_PER_KG.keys()))))] # Show all crops from both lists
    ,use_container_width=True)

    st.subheader("🌟 Mutations & Multipliers")
    st.dataframe(
        [{"Mutation": k, "Multiplier": v} for k, v in MUTATION_MULTIPLIERS.items()]
    ,use_container_width=True)

st.markdown("---")
st.caption("Grow a Garden Fan Tool, By Gregothey.")
st.caption("Prices are rough estimates and may not be exact.")
st.caption("C/KG Will Take Longer To Add For Newer Stuff")
