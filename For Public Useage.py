import streamlit as st

# ✅ MUST BE FIRST
st.set_page_config(page_title="Grow a Garden App", layout="wide")

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
    "Wet": 2, "Chilled": 2, "Chocolate": 2, "Moonlit": 2,
    "Bloodlit": 4, "Plasma": 5, "Frozen": 10, "Golden": 20, "Zombified": 25,
    "Shocked": 50, "Rainbow": 50, "Celestial": 120, "Disco": 125, "Twisted": 30,
    "Pollinated": 32, # Using the second value as requested
    "Voided": 155,
}

# Sort crop names for selectbox consistency
SORTED_CROP_NAMES = sorted(list(BASE_PRICES.keys()))
SORTED_MUTATION_NAMES = sorted(list(MUTATION_MULTIPLIERS.keys()))

# === Helper ===
def calculate_value(crop, units, mutations, calculation_mode):
    initial_value = 0
    try:
        if calculation_mode == "Price per KG":
            base_unit_price = PRICE_PER_KG.get(crop, 0)
            # Ensure units is float for weight calculation
            initial_value = base_unit_price * float(units)
        elif calculation_mode == "Fixed Base Price per Item":
            base_item_price = BASE_PRICES.get(crop, 0)
             # Ensure units is int for quantity calculation
            initial_value = base_item_price * int(units)
        else:
            # This case should ideally not be reached if UI logic is correct
            st.error(f"Internal error: Invalid calculation mode '{calculation_mode}'.")
            return 0
    except ValueError:
        st.error(f"Error: Could not convert units '{units}' to the required number type for {calculation_mode}.")
        return 0


    mutation_multiplier_total = 1
    for m in mutations:
        mutation_multiplier_total *= MUTATION_MULTIPLIERS.get(m, 1)

    return initial_value * mutation_multiplier_total

# === UI ===
st.title("🌿 Grow a Garden - Calculator & Trading App")

tabs = st.tabs(["📈 Calculator", "🔁 Trading", "📚 Values"])

# Initialize session state for radio button default indices if they don't exist
# These store the *index* of the selected option (0 or 1)
if 'calc_mode_main_idx' not in st.session_state:
    st.session_state.calc_mode_main_idx = 0  # Default to "Price per KG"
if 'trade_a_mode_idx' not in st.session_state:
    st.session_state.trade_a_mode_idx = 0
if 'trade_b_mode_idx' not in st.session_state:
    st.session_state.trade_b_mode_idx = 0

# === Calculator Tab ===
with tabs[0]:
    st.header("📈 Value Calculator")
    crop_calc = st.selectbox("Select crop", SORTED_CROP_NAMES, key="crop_calc_select")

    price_for_kg_value_calc = PRICE_PER_KG.get(crop_calc, 0)
    is_price_per_kg_available_calc = price_for_kg_value_calc > 0

    # Determine effective calculation mode and manage radio button state
    radio_options_calc = ("Price per KG", "Fixed Base Price per Item")
    if is_price_per_kg_available_calc:
        # Allow user to choose if Price per KG is available
        chosen_mode_idx_calc = st.radio(
            "Select Calculation Mode:",
            options=radio_options_calc,
            index=st.session_state.calc_mode_main_idx, # Use session state for persistence
            key="calc_mode_main_radio_selector"
        )
        effective_calc_mode = radio_options_calc[chosen_mode_idx_calc]
        st.session_state.calc_mode_main_idx = chosen_mode_idx_calc # Update session state
    else:
        # Force "Fixed Base Price per Item" if Price per KG is 0 or N/A
        effective_calc_mode = "Fixed Base Price per Item"
        st.info(f"'{crop_calc}' has a Price per KG of 0 or is not defined. Using 'Fixed Base Price per Item'.")
        st.session_state.calc_mode_main_idx = 1 # Update session state to reflect forced mode (index of "Fixed Base...")

    # Configure units input based on effective_calc_mode
    if effective_calc_mode == "Fixed Base Price per Item":
        units_label_calc = "Enter quantity (items)"
        units_min_calc = 1      # int
        units_step_calc = 1     # int
        units_format_calc = "%d"
        units_default_calc = 1  # int
    else: # Price per KG
        units_label_calc = "Enter weight (kg)"
        units_min_calc = 0.01    # float, allow smaller weights
        units_step_calc = 0.01   # float
        units_format_calc = "%.2f"
        units_default_calc = 1.0 # float


    units_calc = st.number_input(
        units_label_calc,
        min_value=units_min_calc,
        value=units_default_calc, # Default value is now correctly typed
        step=units_step_calc,
        format=units_format_calc,
        key=f"units_calc_input_{effective_calc_mode.replace(' ', '_')}" # Dynamic key
    )
    mutations_calc = st.multiselect(
        "Mutations (multi-select)",
        SORTED_MUTATION_NAMES,
        key="mutations_calc"
    )

    if st.button("Calculate Value", key="btn_calc"):
        value = calculate_value(crop_calc, units_calc, mutations_calc, effective_calc_mode)
        st.success(f"Total Value: {value:,.2f} coins")


# === Trading Tab ===
with tabs[1]:
    st.header("🔁 Trade Comparison")
    col1, col2 = st.columns(2)
    radio_options_trade = ("Price per KG", "Fixed Base Price per Item")

    # --- Trader A ---
    with col1:
        st.subheader("Trader A")
        crop_a = st.selectbox("Crop A", SORTED_CROP_NAMES, key="crop_a_select")

        price_for_kg_value_a = PRICE_PER_KG.get(crop_a, 0)
        is_price_per_kg_available_a = price_for_kg_value_a > 0

        if is_price_per_kg_available_a:
            chosen_mode_idx_a = st.radio(
                "Calculation Mode A:",
                options=radio_options_trade,
                index=st.session_state.trade_a_mode_idx,
                key="trade_a_mode_radio_selector"
            )
            effective_mode_a = radio_options_trade[chosen_mode_idx_a]
            st.session_state.trade_a_mode_idx = chosen_mode_idx_a
        else:
            effective_mode_a = "Fixed Base Price per Item"
            st.info(f"A: '{crop_a}' has Price/KG of 0 or N/A. Using 'Fixed Base Price'.")
            st.session_state.trade_a_mode_idx = 1


        if effective_mode_a == "Fixed Base Price per Item":
            units_label_a, units_min_a, units_step_a, units_format_a, units_default_a = ("Quantity A (items)", 1, 1, "%d", 1)
        else: # Price per KG
            units_label_a, units_min_a, units_step_a, units_format_a, units_default_a = ("Weight A (kg)", 0.01, 0.01, "%.2f", 1.0)

        units_a = st.number_input(units_label_a, min_value=units_min_a, value=units_default_a, step=units_step_a, format=units_format_a, key=f"units_a_input_{effective_mode_a.replace(' ', '_')}")
        muts_a = st.multiselect("Mutations A", SORTED_MUTATION_NAMES, key="ma_select")

    # --- Trader B ---
    with col2:
        st.subheader("Trader B")
        crop_b = st.selectbox("Crop B", SORTED_CROP_NAMES, key="crop_b_select")

        price_for_kg_value_b = PRICE_PER_KG.get(crop_b, 0)
        is_price_per_kg_available_b = price_for_kg_value_b > 0

        if is_price_per_kg_available_b:
            chosen_mode_idx_b = st.radio(
                "Calculation Mode B:",
                options=radio_options_trade,
                index=st.session_state.trade_b_mode_idx,
                key="trade_b_mode_radio_selector"
            )
            effective_mode_b = radio_options_trade[chosen_mode_idx_b]
            st.session_state.trade_b_mode_idx = chosen_mode_idx_b
        else:
            effective_mode_b = "Fixed Base Price per Item"
            st.info(f"B: '{crop_b}' has Price/KG of 0 or N/A. Using 'Fixed Base Price'.")
            st.session_state.trade_b_mode_idx = 1


        if effective_mode_b == "Fixed Base Price per Item":
            units_label_b, units_min_b, units_step_b, units_format_b, units_default_b = ("Quantity B (items)", 1, 1, "%d", 1)
        else: # Price per KG
            units_label_b, units_min_b, units_step_b, units_format_b, units_default_b = ("Weight B (kg)", 0.01, 0.01, "%.2f", 1.0)

        units_b = st.number_input(units_label_b, min_value=units_min_b, value=units_default_b, step=units_step_b, format=units_format_b, key=f"units_b_input_{effective_mode_b.replace(' ', '_')}")
        muts_b = st.multiselect("Mutations B", SORTED_MUTATION_NAMES, key="mb_select")


    if st.button("Compare Trade", key="btn_compare"):
        val_a = calculate_value(crop_a, units_a, muts_a, effective_mode_a)
        val_b = calculate_value(crop_b, units_b, muts_b, effective_mode_b)

        st.write(f"💰 Trader A Value: `{val_a:,.2f}` coins")
        st.write(f"💰 Trader B Value: `{val_b:,.2f}` coins")

        diff = abs(val_a - val_b)
        # Consider a threshold for fairness, e.g., 10% of the higher value
        # Handle cases where one or both values might be zero to avoid division by zero
        max_val = max(val_a, val_b)
        threshold = max_val * 0.1 if max_val > 0 else 0

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
    # Create a comprehensive list of all crop names from both dictionaries
    all_crop_keys = sorted(list(set(list(BASE_PRICES.keys()) + list(PRICE_PER_KG.keys()))))
    data_for_df = []
    for k in all_crop_keys:
        data_for_df.append({
            "Crop": k,
            "Base Price (per item)": BASE_PRICES.get(k, "N/A"), # Use .get for safety
            "Price per KG": PRICE_PER_KG.get(k, "N/A")    # Use .get for safety
        })
    st.dataframe(data_for_df, use_container_width=True)

    st.subheader("🌟 Mutations & Multipliers")
    st.dataframe(
        [{"Mutation": k, "Multiplier": v} for k, v in sorted(MUTATION_MULTIPLIERS.items())],
        use_container_width=True
    )

st.markdown("---")
st.caption("Grow a Garden Fan Tool, By Gregothey.")
st.caption("Prices are rough estimates and may not be exact.")
st.caption("C/KG Will Take Longer To Add For Newer Stuff")
