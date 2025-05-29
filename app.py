import tkinter as tk
from tkinter import ttk

# Base prices for crops
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
    "Apple": 400,  # Average of 300–500
    "Grape": 10000,
    "Venus Fly Trap": 15000,
    "Mango": 6500,
    "Dragon Fruit": 4750,
    "Cursed Fruit": 50000,  # Average of 20,000–80,000
    "Soul Fruit": 10500,    # Average of 5,000–16,000
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
}

# Mutations that can stack to form another mutation
STACKABLE_MUTATIONS = {
    frozenset(["Wet", "Chilled"]): "Frozen",
}

class GrowAGardenCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Grow a Garden Calculator")

        # Crop selection
        self.crop_label = ttk.Label(root, text="Select Crop:")
        self.crop_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.selected_crop = tk.StringVar()
        self.crop_combobox = ttk.Combobox(root, textvariable=self.selected_crop)
        self.crop_combobox['values'] = list(CROP_PRICES.keys())
        self.crop_combobox.grid(row=0, column=1, padx=10, pady=10)

        # Mutations selection
        self.mutation_label = ttk.Label(root, text="Select Mutations:")
        self.mutation_label.grid(row=1, column=0, padx=10, pady=10, sticky="nw")

        self.mutation_vars = {}
        self.mutation_checks = {}
        for idx, mutation in enumerate(MUTATION_MULTIPLIERS.keys()):
            var = tk.BooleanVar()
            chk = ttk.Checkbutton(root, text=mutation, variable=var)
            chk.grid(row=1 + idx // 4, column=1 + idx % 4, padx=5, pady=5, sticky="w")
            self.mutation_vars[mutation] = var
            self.mutation_checks[mutation] = chk

        # Calculate button
        self.calculate_button = ttk.Button(root, text="Calculate Value", command=self.calculate_value)
        self.calculate_button.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

        # Result display
        self.result_label = ttk.Label(root, text="Final Value: ₵0")
        self.result_label.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

    def calculate_value(self):
        crop = self.selected_crop.get()
        if crop not in CROP_PRICES:
            self.result_label.config(text="Please select a valid crop.")
            return

        base_price = CROP_PRICES[crop]
        selected_mutations = [mutation for mutation, var in self.mutation_vars.items() if var.get()]

        # Handle stacking mutations
        mutations_to_apply = set(selected_mutations)
        for combo, result in STACKABLE_MUTATIONS.items():
            if combo.issubset(mutations_to_apply):
                mutations_to_apply.difference_update(combo)
                mutations_to_apply.add(result)

        # Calculate final multiplier
        final_multiplier = 1
        for mutation in mutations_to_apply:
            multiplier = MUTATION_MULTIPLIERS.get(mutation, 1)
            final_multiplier *= multiplier

        final_value = base_price * final_multiplier
        self.result_label.config(text=f"Final Value: ₵{final_value:,}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GrowAGardenCalculator(root)
    root.mainloop()
