import json
import random
import sys
import os
from datetime import date
from time import sleep
from colorama import Fore, Style

from options import RATIONS_CONSOLE_PREFIX
from functions.helpers import random_ending, random_food_ending
from functions.os import get_resource_path, loading_ellipsis, menu_prompt, typed_input, typed_print

# ----------------------------- #
#          CONSTANTS            #
# ----------------------------- #

MAX_SERVINGS_PER_INGREDIENT = 3
MEALS_PER_WEEK = 14
DAYS_PER_WEEK = 7
RNG = None
INGREDIENTS = None

BOUNDS = {
    "energy": [x * 4.184 * 7 for x in [1600, 1850]],  # kJ/week
    "carbohydrates": [0, 140],                       # g/week
    "protein": 180 * 7                               # g/week
}

IGNORED_INGREDIENTS = [30, 29, 38]  # Filet, T-Bone, Tuna (water)
IGNORED_EXCLUSIONS = ["Brussels Sprouts",
                      "Cauliflower", "Mushrooms", "Endives"]

# ----------------------------- #
#        RATIONING CORE         #
# ----------------------------- #


def update_rations(name):
    typed_print(
        f"{RATIONS_CONSOLE_PREFIX}Preparing rationing data", newline=False)
    for _ in range(3):
        loading_ellipsis(length=1, sleep_for=0.7)

    year, week, _ = date.today().isocalendar()
    seed = int(f"{year}{week:02d}")

    print()
    typed_print(f"{RATIONS_CONSOLE_PREFIX}Data successfully loaded!")

    mode = menu_prompt([
        {"title": "curr", "description": "Get this current week's rations"},
        {"title": "prep", "description": "Get next week's rations"}
    ], title="mode")

    if mode in ("exit", None):
        print()
        return random_ending(name)

    week_offset = 1 if mode == "prep" else 0
    rng = random.Random(seed + week_offset)

    typed_print(f"{RATIONS_CONSOLE_PREFIX}Retrieving rations", newline=False)
    loading_ellipsis(length=2, sleep_for=0.7)

    ingredients = get_ingredients(rng)

    loading_ellipsis(length=1, sleep_for=0.7)
    print()
    typed_print(
        f"{RATIONS_CONSOLE_PREFIX}Successfully retrieved rations for {'next week' if week_offset else 'this week'}:")
    typed_print(f"{render_ingredients(ingredients)}\n")

    return random_food_ending(name)

# ----------------------------- #
#         GENERATION            #
# ----------------------------- #


def get_ingredients(rng):
    global RNG
    RNG = rng
    return next(i for i in iter(generate_ingredients, None) if check_ingredients(i))


def generate_ingredients():
    global INGREDIENTS
    with open(get_resource_path("data/rations.json"), "r") as file:
        raw_data = json.load(file)

    INGREDIENTS = [
        ing for ing in raw_data["ingredients"]
        if ing["id"] not in IGNORED_INGREDIENTS
    ]
    raw_exclusions = raw_data["exclusions"]

    fixed = get_fixed_ingredients()
    proteins = generate_protein_ingredients()

    exclusions = sorted(
        RNG.sample(
            [v for v in raw_exclusions["vegetables"]
             if v not in IGNORED_EXCLUSIONS + ["Onions", "Cucumbers", "Tomatoes", "Mixed Leaves"]],
            4
        ) + ["Onions", "Cucumbers", "Tomatoes", "Mixed Leaves"]
    )

    all_ingredients = sorted(
        fixed + proteins, key=lambda ing: get_ingredient_from_id(INGREDIENTS, ing["id"])["name"])

    totals = {"energy": 0, "protein": 0, "carbs": 0}
    for ing in all_ingredients:
        info = get_ingredient_from_id(INGREDIENTS, ing["id"])
        s, n = info["serving"] * info["conversion"], info["nutrition"]
        totals["energy"] += s * n["energy"] * ing["servings"]
        totals["protein"] += s * n["protein"] * ing["servings"]
        totals["carbs"] += s * n["carbohydrate"]["total"] * ing["servings"]

    return {
        "energy": totals["energy"],
        "protein": {
            "total": totals["protein"],
            "ingredients": [format_ingredient(i, "proteins") for i in all_ingredients]
        },
        "non_protein": [format_ingredient(i, "non-proteins") for i in all_ingredients],
        "carbohydrate": totals["carbs"],
        "exclusions": exclusions
    }


def get_fixed_ingredients():
    return [
        {"id": 11, "servings": 7},   # Olive Oil
        {"id": 10, "servings": 7},   # Butter
        {"id": 44, "servings": 2},   # Pasta Sauce
        {"id": 20, "servings": 24},  # Eggs
        {"id": 46, "servings": 7},   # Protein Powder
        {"id": RNG.choice([i["id"] for i in INGREDIENTS if i["subcategory"]
                          == "Dairy-Based fats"]), "servings": 3},
        {"id": RNG.choice([i["id"] for i in INGREDIENTS if i["subcategory"]
                          == "Plant-Based fats"]), "servings": 2},
        *[
            {"id": cid, "servings": 4}
            for cid in RNG.sample([i["id"] for i in INGREDIENTS if i["subcategory"] == "Cheeses"], 2)
        ],
        *[
            {"id": i["id"], "servings": 2}
            for i in INGREDIENTS if i["subcategory"] == "Fatty Meats" and RNG.random() < 0.48
        ]
    ]


def generate_protein_ingredients():
    proteins = [i["id"] for i in INGREDIENTS if i["category"] ==
                "proteins" and i["id"] != 20 and i["subcategory"] != "Cheeses"]
    RNG.shuffle(proteins)
    beef = [i["id"] for i in INGREDIENTS if i["subcategory"] == "Beef"]
    selected_beef = RNG.sample(beef, min(2, len(beef)))
    non_beef = RNG.sample(
        [p for p in proteins if p not in beef], 5 - len(selected_beef))
    selected = selected_beef + non_beef[:5]

    return [{"id": pid, "servings": 3 if i < 4 else 2} for i, pid in enumerate(selected)]


def check_ingredients(data):
    return (
        data["protein"]["total"] >= BOUNDS["protein"]
        and BOUNDS["energy"][0] <= data["energy"] <= BOUNDS["energy"][1]
        and data["carbohydrate"] <= BOUNDS["carbohydrates"][1]
    )


def get_ingredient_from_id(ingredients, ing_id):
    return next((ing for ing in ingredients if ing["id"] == ing_id), None)


def format_ingredient(ingredient, category_filter):
    ing = get_ingredient_from_id(INGREDIENTS, ingredient["id"])
    if ((category_filter == "proteins" and ing["category"] != "proteins") or
            (category_filter == "non-proteins" and ing["category"] == "proteins")):
        return None
    return {
        "name": ing["name"],
        "servings": ingredient["servings"],
        "units": ing["unit"],
        "conversion": ing["conversion"],
        "serving": ing["serving"]
    }

# ----------------------------- #
#         DISPLAYING            #
# ----------------------------- #


def format_serving(amount, unit):
    plural_units = {"egg", "cup", "scoop", "can",
                    "slice", "tablespoon", "teaspoon", "piece"}
    if unit in plural_units and amount != 1:
        unit += "s"
    return f"{round(amount, 2)} {unit}"


def get_ingredient_table(ingredients_list):
    rows = []
    for ing in filter(None, ingredients_list):
        total_weight = round(
            ing["servings"] * ing["serving"] * ing["conversion"] * 100)
        rows.append((ing["name"], ing["servings"], format_serving(
            ing["serving"], ing["units"]), f"{total_weight} g"))
    return rows


def render_ingredients(data):
    energy_kj = data["energy"]
    energy_cal = energy_kj / 4.184
    daily_energy = energy_kj / DAYS_PER_WEEK
    daily_protein = data["protein"]["total"] / DAYS_PER_WEEK

    protein_rows = get_ingredient_table(data["protein"]["ingredients"])
    non_protein_rows = get_ingredient_table(data["non_protein"])

    def format_section(title, rows):
        header = f"{'Ingredient':<30} {'Servings':<10} {'Serving Size':<20} {'Total Weight':<15}"
        lines = [
            f"\n{Fore.YELLOW}{Style.BRIGHT}{title}{Style.RESET_ALL}",
            f"{Fore.YELLOW}{'-' * len(title)}{Style.RESET_ALL}",
            f"{Fore.YELLOW}{header}{Style.RESET_ALL}",
            f"{Fore.YELLOW}{'-' * len(header)}{Style.RESET_ALL}",
        ]
        for name, servings, size, weight in rows:
            lines.append(f"{name:<30} {servings:<10} {size:<20} {weight:<15}")
        return "\n".join(lines)

    summary = [
        f"{Fore.YELLOW}Total Energy:{Style.RESET_ALL}        {Style.BRIGHT}{energy_kj:.2f} kJ{Style.RESET_ALL} ({energy_cal:.2f} cal)",
        f"{Fore.YELLOW}Daily Energy:{Style.RESET_ALL}        {Style.BRIGHT}{daily_energy:.2f} kJ{Style.RESET_ALL} ({daily_energy / 4.184:.2f} cal)",
        f"{Fore.YELLOW}Total Protein:{Style.RESET_ALL}       {Style.BRIGHT}{data['protein']['total']:.2f} g{Style.RESET_ALL} ({daily_protein:.2f} g/day)",
        f"{Fore.YELLOW}Total Carbohydrates:{Style.RESET_ALL} {Style.BRIGHT}{data['carbohydrate']:.2f} g{Style.RESET_ALL}",
        format_section("Protein Ingredients", protein_rows),
        format_section("Non-Protein Ingredients", non_protein_rows),
        f"\n{Fore.YELLOW}Unlimited:{Style.RESET_ALL} {', '.join(data['exclusions'][:-1])} and {data['exclusions'][-1]}"
    ]

    return "\n".join(summary)
