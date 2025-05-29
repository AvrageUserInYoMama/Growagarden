import streamlit as st
import random

# Data: prices, mutations, stackables
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

# Helper: apply stackable mutations
def apply_stackable_mutations(selected_mutations):
    mutations = set(selected_mutations)
    for combo, result in STACKABLE_MUTATIONS.items():
        if combo.issubset(mutations):
            mutations.difference_update(combo)
            mutations.add(result)
    return list(mutations)

# Calculate total value of an item
def calculate_value(name, base_price, weight, method, mutations):
    mutations = apply_stackable_mutations(mutations)
    multiplier = sum(MUTATION_MULTIPLIERS.get(m, 0) for m in mutations)
    if method == "Weight-based":
        price_per_kg = PRICE_PER_KG.get(name, base_price)  # fallback to base price if not found
        total = weight * price_per_kg * (1 + multiplier)
    else:
        total = base_price * (1 + multiplier)
    return total

# --- Streamlit UI ---
st.title("Grow a Garden Crop & Trading Calculator")

# Mode selector: normal / trading
trading_mode = st.checkbox("Enable Trading Mode")

if not trading_mode:
    # Normal mode: single crop value calc

    crop = st.selectbox("Select a Crop", list(CROP_PRICES.keys()))
    custom_mode = st.checkbox("Custom Mode (Set your own item & price)", key="custom_mode_main")

    if custom_mode:
        custom_name = st.text_input("Custom Item Name", key="custom_name_main")
        custom_price = st.number_input("Custom Base Price (₵)", min_value=0.0, format="%.2f", key="custom_price_main")
        calculation_method = st.radio("Calculation Method", ["Weight-based", "Base Price"], key="custom_method_main")

        if calculation_method == "Weight-based":
            weight = st.number_input("Weight (kg)", min_value=0.0, format="%.2f", key="custom_weight_main")
        else:
            weight = 1.0  # Dummy weight for base price calc

        mutations = st.multiselect("Select Mutation(s)", list(MUTATION_MULTIPLIERS.keys()), key="custom_mutations_main")

        total_value = calculate_value(custom_name or "Custom Item", custom_price, weight, calculation_method, mutations)
    else:
        weight = st.number_input("Weight (kg)", min_value=0.0, format="%.2f", key="weight_main")
        mutations = st.multiselect("Select Mutation(s)", list(MUTATION_MULTIPLIERS.keys()), key="mutations_main")

        total_value = calculate_value(crop, CROP_PRICES.get(crop, 0), weight, "Weight-based", mutations)

    st.subheader(f"Total Value: ₵{total_value:,.2f}")

else:
    # Trading mode: two offers of 3 items each
    st.header("Trading Mode")
    custom_mode_trade = st.checkbox("Enable Custom Items in Trading", key="custom_mode_trade")

    def render_trade_side(prefix):
        st.subheader(f"{prefix} Offer")

        items = []
        for i in range(3):
            st.markdown(f"### Item {i+1}")

            use_custom = False
            if custom_mode_trade:
                use_custom = st.checkbox(f"Custom Item?", key=f"{prefix}_custom_{i}")

            if use_custom:
                item_name = st.text_input(f"Custom Item Name - {prefix} {i+1}", key=f"{prefix}_custom_name_{i}")
                item_base_price = st.number_input(f"Base Price (₵) - {prefix} {i+1}", min_value=0.0, format="%.2f", key=f"{prefix}_custom_price_{i}")
                item_weight = st.number_input(f"Weight (kg) - {prefix} {i+1}", min_value=0.0, format="%.2f", key=f"{prefix}_custom_weight_{i}")
                method = st.radio(f"Calculation Method - {prefix} {i+1}", ["Weight-based", "Base Price"], key=f"{prefix}_custom_method_{i}")
            else:
                item_name = st.selectbox(f"Select Crop - {prefix} {i+1}", list(CROP_PRICES.keys()), key=f"{prefix}_crop_{i}")
                item_base_price = CROP_PRICES.get(item_name, 0)
                item_weight = st.number_input(f"Weight (kg) - {prefix} {i+1}", min_value=0.0, format="%.2f", key=f"{prefix}_weight_{i}")
                method = "Weight-based"

            item_mutations = st.multiselect(f"Mutations - {prefix} {i+1}", list(MUTATION_MULTIPLIERS.keys()), key=f"{prefix}_mutations_{i}")

            item_value = calculate_value(item_name, item_base_price, item_weight, method, item_mutations)
            st.write(f"Value: ₵{item_value:,.2f}")

            items.append(item_value)

        return sum(items)

    your_total = render_trade_side("Your")
    their_total = render_trade_side("Their")

    st.markdown("---")
    st.subheader("Trade Summary")
    st.write(f"**Your offer total value:** ₵{your_total:,.2f}")
    st.write(f"**Their offer total value:** ₵{their_total:,.2f}")

    diff = their_total - your_total

    if diff > 50:
        st.success("Win! Their offer is worth more than yours.")
    elif abs(diff) <= 50:
        st.info("Fair trade! Offers are close in value.")
    else:
        st.error("Loss! Your offer is worth more than theirs.")

# Footer disclaimers
st.markdown("---")
st.markdown("🔹 **Not affiliated with _The Garden Game_ or the Grow a Garden developers. This is a fan-made tool.**")
st.markdown("🔹 **Prices are rough estimates.**")
st.markdown("🔹 **Made by Gregothey.**")

