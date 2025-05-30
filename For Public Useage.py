import streamlit as st
import uuid
from streamlit_autorefresh import st_autorefresh

# --- Constants ---

# Price per kilogram for each crop
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

# List of crops
CROPS = list(PRICE_PER_KG.keys())

# --- Initialize Session State ---

if "messages" not in st.session_state:
    st.session_state.messages = []  # For chat messages in trade

if "trades" not in st.session_state:
    st.session_state.trades = {}  # Stores all trade sessions and their offers

if "current_trade_code" not in st.session_state:
    st.session_state.current_trade_code = None  # Current trade session code


# --- Helper Functions ---

def calculate_offer_value(crop, weight_kg, selected_mutations):
    """Calculate the total value of the offer given crop, weight, and mutations."""
    base_price = PRICE_PER_KG.get(crop, 0)
    multiplier = 1
    for m in selected_mutations:
        multiplier *= MUTATION_MULTIPLIERS.get(m, 1)
    total_value = base_price * weight_kg * multiplier
    return total_value, multiplier

def create_new_trade():
    """Create a new trade session with a unique code."""
    trade_code = str(uuid.uuid4())[:8]  # 8 char unique code
    st.session_state.trades[trade_code] = {
        "offers": [],  # list of dict offers
        "messages": []
    }
    st.session_state.current_trade_code = trade_code
    return trade_code

def join_trade(trade_code):
    """Join an existing trade if code exists."""
    if trade_code in st.session_state.trades:
        st.session_state.current_trade_code = trade_code
        return True
    return False

def add_offer_to_trade(trade_code, offer):
    """Add an offer dict to the trade's offers list."""
    st.session_state.trades[trade_code]["offers"].append(offer)

def add_message_to_trade(trade_code, message):
    """Add a message string to the trade's messages list."""
    st.session_state.trades[trade_code]["messages"].append(message)

# --- UI ---

st.title("🌱 Grow a Garden - Trade & Crop Calculator")

# Section: Trade Management
st.header("Trade Session")

col1, col2 = st.columns(2)

with col1:
    if st.button("Create New Trade Session"):
        code = create_new_trade()
        st.success(f"Created new trade session with code: {code}")

with col2:
    join_code_input = st.text_input("Enter Trade Code to Join")
    if st.button("Join Trade"):
        if join_trade(join_code_input.strip()):
            st.success(f"Joined trade session: {join_code_input.strip()}")
        else:
            st.error("Trade code not found. Please check and try again.")

current_trade_code = st.session_state.current_trade_code
if current_trade_code:
    st.info(f"Current Trade Code: **{current_trade_code}** - Share this code with your trading partner.")

# If no trade session selected, ask to create/join first
if not current_trade_code:
    st.warning("Please create or join a trade session to continue.")
    st.stop()

# Section: Add Offer
st.header("Add Your Offer")

selected_crop = st.selectbox("Select Crop", CROPS)
weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1, format="%.2f")

selected_mutations = st.multiselect(
    "Select Mutations (multiple allowed)",
    options=list(MUTATION_MULTIPLIERS.keys())
)

if st.button("Add Offer to Trade"):
    if weight <= 0:
        st.error("Please enter a valid weight greater than zero.")
    else:
        value, total_multiplier = calculate_offer_value(selected_crop, weight, selected_mutations)
        offer = {
            "crop": selected_crop,
            "weight": weight,
            "mutations": selected_mutations,
            "multiplier": total_multiplier,
            "value": value,
        }
        add_offer_to_trade(current_trade_code, offer)
        st.success(f"Offer added: {selected_crop} ({weight} kg) with multiplier {total_multiplier}x worth {value:.2f}")

# Section: View Current Offers
st.header("Current Trade Offers")

offers = st.session_state.trades[current_trade_code]["offers"]

if offers:
    for idx, offer in enumerate(offers):
        st.markdown(f"**Offer {idx+1}:** {offer['crop']} — {offer['weight']} kg — Mutations: {', '.join(offer['mutations']) if offer['mutations'] else 'None'} — Multiplier: {offer['multiplier']}x — Value: {offer['value']:.2f}")
else:
    st.info("No offers added yet.")

# Section: Messaging (with auto refresh every 3 seconds)
st.header("Trade Chat")

# Autorefresh messages every 3 seconds
st_autorefresh(interval=3000, key="message_refresh")

messages = st.session_state.trades[current_trade_code]["messages"]

for msg in messages:
    st.write(msg)

new_message = st.text_input("Enter message")
if st.button("Send Message"):
    if new_message.strip():
        add_message_to_trade(current_trade_code, new_message.strip())
        st.experimental_rerun()

