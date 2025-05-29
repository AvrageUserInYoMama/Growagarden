import streamlit as st
import random
from datetime import datetime

# ... (keep all your price dictionaries and helper functions here, unchanged)

def calculate_item_value(crop, weight, base_price, mutations, method):
    mutations_to_apply = set(mutations)
    for combo, result in STACKABLE_MUTATIONS.items():
        if combo.issubset(mutations_to_apply):
            mutations_to_apply.difference_update(combo)
            mutations_to_apply.add(result)
    if method == "Base Price":
        base = base_price
    else:
        base = PRICE_PER_KG.get(crop, 0) * weight
    final_multiplier = sum(MUTATION_MULTIPLIERS.get(m, 0) for m in mutations_to_apply)
    return base * (1 + final_multiplier)

def calculate_trade_total(offers):
    total = 0.0
    for item in offers:
        if item["use_custom"]:
            val = item["custom_price"]
        else:
            val = calculate_item_value(
                item["crop"], item["weight"], item["base_price"], item["mutations"], item["method"]
            )
        total += val
    return total

st.title("Grow a Garden Crop Value Calculator & Trading Mode with Chat")

if "trades" not in st.session_state:
    st.session_state.trades = {}

if "roblox_username" not in st.session_state:
    st.session_state.roblox_username = ""

trading_mode = st.checkbox("Enable Trading Mode")

if not trading_mode:
    st.write("Trading mode is off. Use this mode to calculate crop value.")
    crop = st.selectbox("Select a Crop", list(CROP_PRICES.keys()))
    weight = st.number_input("Enter Weight (kg)", min_value=0.0, format="%.2f")
    base_price_input = st.number_input("Or Base Price (₵)", min_value=0.0, format="%.2f", value=0.0)
    selected_mutations = st.multiselect("Select Mutation(s)", list(MUTATION_MULTIPLIERS.keys()))
    method = "Base Price" if base_price_input > 0 else "Weight-based"
    total_value = calculate_item_value(crop, weight, base_price_input, selected_mutations, method)
    st.subheader(f"Total Value: ₵{total_value:,.2f}")
else:
    st.header("Trading Mode")

    # Offer inputs (same as before)
    def trade_item_input(prefix):
        use_custom = st.checkbox(f"Use custom price and name for {prefix} item?", key=f"{prefix}_use_custom")
        if use_custom:
            custom_name = st.text_input(f"{prefix} Custom Item Name", key=f"{prefix}_custom_name")
            custom_price = st.number_input(f"{prefix} Custom Item Price (₵)", min_value=0.0, format="%.2f", key=f"{prefix}_custom_price")
            return {
                "use_custom": True,
                "custom_name": custom_name if custom_name else "Custom Item",
                "custom_price": custom_price,
                "crop": "",
                "weight": 0.0,
                "base_price": 0.0,
                "mutations": [],
                "method": "Base Price",
            }
        else:
            crop = st.selectbox(f"{prefix} Crop", list(CROP_PRICES.keys()), key=f"{prefix}_crop")
            weight = st.number_input(f"{prefix} Weight (kg)", min_value=0.0, format="%.2f", key=f"{prefix}_weight")
            base_price = st.number_input(f"{prefix} Base Price (₵, 0 to ignore)", min_value=0.0, format="%.2f", key=f"{prefix}_base_price")
            mutations = st.multiselect(f"{prefix} Mutations", list(MUTATION_MULTIPLIERS.keys()), key=f"{prefix}_mutations")
            method = "Base Price" if base_price > 0 else "Weight-based"
            return {
                "use_custom": False,
                "custom_name": "",
                "custom_price": 0.0,
                "crop": crop,
                "weight": weight,
                "base_price": base_price,
                "mutations": mutations,
                "method": method,
            }

    st.subheader("Your Offer")
    your_offers = []
    for i in range(3):
        st.markdown(f"### Item {i+1}")
        your_offers.append(trade_item_input(f"Your_{i}"))

    st.subheader("Their Offer")
    their_offers = []
    for i in range(3):
        st.markdown(f"### Item {i+1}")
        their_offers.append(trade_item_input(f"Their_{i}"))

    your_total = calculate_trade_total(your_offers)
    their_total = calculate_trade_total(their_offers)

    st.markdown(f"**Your Offer Total Value:** ₵{your_total:,.2f}")
    st.markdown(f"**Their Offer Total Value:** ₵{their_total:,.2f}")

    st.markdown("---")
    st.subheader("Trade Session")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Generate New Trade ID"):
            if not st.session_state.roblox_username:
                username_input = st.text_input("Enter your Roblox username to generate trade ID:", key="gen_username")
                if username_input.strip():
                    st.session_state.roblox_username = username_input.strip()
                    st.experimental_rerun()
                else:
                    st.warning("You must enter a Roblox username to generate a trade ID.")
            else:
                trade_id = str(random.randint(1000000000, 9999999999))
                st.session_state.trades[trade_id] = {
                    "your_offers": your_offers,
                    "their_offers": their_offers,
                    "your_total": your_total,
                    "their_total": their_total,
                    "chat": [],
                    "users": [st.session_state.roblox_username],
                }
                st.session_state.trade_id = trade_id
                st.success(f"New Trade ID generated: {trade_id}")

    with col2:
        load_id = st.text_input("Or enter existing Trade ID to join/load", key="load_trade_id")
        if load_id:
            if not st.session_state.roblox_username:
                username_input = st.text_input("Enter your Roblox username to join trade:", key="join_username")
                if username_input.strip():
                    st.session_state.roblox_username = username_input.strip()
                    st.experimental_rerun()
                else:
                    st.warning("You must enter a Roblox username to join a trade.")
            else:
                if load_id in st.session_state.trades:
                    st.session_state.trade_id = load_id
                    if st.session_state.roblox_username not in st.session_state.trades[load_id]["users"]:
                        st.session_state.trades[load_id]["users"].append(st.session_state.roblox_username)
                    st.success(f"Loaded Trade ID: {load_id}")
                else:
                    st.warning("Trade ID not found.")

    # Show trade and chat if trade_id set
    if "trade_id" in st.session_state:
        trade_id = st.session_state.trade_id
        trade_data = st.session_state.trades[trade_id]
        st.markdown(f"## Trade ID: {trade_id}")
        st.markdown(f"**Participants:** {', '.join(trade_data['users'])}")

        # Offer summaries
        st.markdown("### Offer Summary")
        def offer_summary(offers):
            lines = []
            for i, item in enumerate(offers):
                if item["use_custom"]:
                    lines.append(f"{item['custom_name']} at ₵{item['custom_price']:.2f}")
                else:
                    lines.append(f"{item['crop']} ({item['weight']}kg, Mutations: {', '.join(item['mutations']) if item['mutations'] else 'None'})")
            return lines

        st.markdown("**Your Offer:**")
        for line in offer_summary(trade_data["your_offers"]):
            st.write(f"- {line}")

        st.markdown("**Their Offer:**")
        for line in offer_summary(trade_data["their_offers"]):
            st.write(f"- {line}")

        st.markdown(f"Your Offer Total: ₵{trade_data['your_total']:.2f}")
        st.markdown(f"Their Offer Total: ₵{trade_data['their_total']:.2f}")

        # Chat section
        st.markdown("---")
        st.subheader("Trade Chat")
        if "chat" not in trade_data:
            trade_data["chat"] = []
        for msg in trade_data["chat"]:
            st.markdown(f"**{msg['user']}:** {msg['message']}")

        new_msg = st.text_input("Type your message:", key="chat_input")
        if st.button("Send", key="send_chat_btn") and new_msg.strip():
            trade_data["chat"].append({
                "user": st.session_state.roblox_username,
                "message": new_msg.strip(),
                "timestamp": datetime.now().isoformat(),
            })
            # Workaround for rerun
            st.session_state["rerun_flag"] = not st.session_state.get("rerun_flag", False)
            st.experimental_rerun()
