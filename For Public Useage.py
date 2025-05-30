import streamlit as st
from streamlit_autorefresh import st_autorefresh

# Define base prices for crops
CROP_PRICES = {
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

# Define price per kilogram for crops
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

# Define mutation multipliers
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

# Function to calculate the value of a crop
def calculate_value(crop, weight, mutation, use_weight, custom_price=None):
    if use_weight:
        base_price = custom_price if custom_price is not None else PRICE_PER_KG.get(crop, 0)
        total = weight * base_price
    else:
        base_price = custom_price if custom_price is not None else CROP_PRICES.get(crop, 0)
        total = base_price

    mutation_multiplier = MUTATION_MULTIPLIERS.get(mutation, 1)
    return total * mutation_multiplier

# Function to summarize trade offers
def summarize_trade(offers, use_weight):
    return sum(calculate_value(*offer, use_weight) for offer in offers)

# Function to get offer input from user
def get_offer_input(prefix):
    offers = []
    for i in range(3):
        cols = st.columns([2, 1, 2, 1])
        crop = cols[0].selectbox(f"{prefix} Crop {i+1}", list(CROP_PRICES.keys()), key=f"{prefix}_crop_{i}")
        weight = cols[1].number_input("Weight", min_value=0.0, step=0.1, key=f"{prefix}_wt_{i}")
        mut = cols[2].selectbox("Mutation", list(MUTATION_MULTIPLIERS.keys()), key=f"{prefix}_mut_{i}")
        price = cols[3].number_input("Custom Price", min_value=0.0, step=0.1, key=f"{prefix}_price_{i}")
        offers.append((crop, weight, mut, price if price > 0 else None))
    return offers

# Main application
def main():
    st.title("Grow a Garden - Crop Calculator and Trading App")

    # Auto-refresh messages every 3 seconds
    st_autorefresh(interval=3000, limit=None, key="auto_refresh")

    # Mode selection
    mode = st.sidebar.selectbox("Select Mode", ["Calculator Mode", "Trading Mode"])

    if mode == "Calculator Mode":
        st.header("Crop Value Calculator")
        use_weight = st.checkbox("Use weight-based values?", value=True)
        crop = st.selectbox("Select Crop", list(CROP_PRICES.keys()))
        weight = st.number_input("Enter Weight (kg)", min_value=0.0, step=0.1)
        mutation = st.selectbox("Select Mutation", list(MUTATION_MULTIPLIERS.keys()))
        custom_price = st.number_input("Enter Custom Price (optional)", min_value=0.0, step=0.1)

        value = calculate_value(crop, weight, mutation, use_weight, custom_price if custom_price > 0 else None)
        st.write(f"Total Value: {value:.2f}")

    elif mode == "Trading Mode":
        st.header("Trade Offers")
        use_weight = st.checkbox("Use weight-based values?", value=True)

        st.subheader("Your Offer")
        your_offer = get_offer_input("your")

        st.subheader("Their Offer")
        their_offer = get_offer_input("their")

        your_val = summarize_trade(your_offer, use_weight)
        their_val = summarize_trade(their_offer, use_weight)

        st.write(f"Your Offer Total Value: {your_val:.2f}")
        st.write(f"Their Offer Total Value: {their_val:.2f}")

        if your_val > their_val:
            st.success("Your offer is more valuable.")
        elif your_val < their_val:
            st.warning("Their offer is more valuable.")
        else:
            st.info("Both offers are equal in value.")

if __name__ == "__main__":
    main()
