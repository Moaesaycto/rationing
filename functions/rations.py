from textwrap import wrap
from tabulate import tabulate
import json
import random
import sys
import os
from datetime import date
from time import sleep
from colorama import Fore, Style

from options import DEFAULT_WIDTH, RATIONS_CONSOLE_PREFIX
from functions.helpers import random_ending, random_food_ending
from functions.os import get_resource_path, hr, loading_ellipsis, menu_prompt, pad_between, subtitle, typed_input, typed_print

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
             if v not in IGNORED_EXCLUSIONS + ["Onions", "Cucumbers", "Tomatoes", "Mixed Leaves", "Spinach"]],
            4
        ) + ["Onions", "Cucumbers", "Tomatoes", "Mixed Leaves", "Spinach"]
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
        {"id": 50, "servings": 7},
        {"id": RNG.choice([i["id"] for i in INGREDIENTS if i["subcategory"]
                          == "Dairy-Based fats"]), "servings": 3},
        {"id": 13, "servings": 2},
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

    # Define column widths (must sum to DEFAULT_WIDTH)
    col_widths = [int(DEFAULT_WIDTH * p) for p in [0.35, 0.1, 0.25, 0.3]]

    def pad_cell(content, width, align="left"):
        content = str(content)
        if len(content) > width:
            return content[:width]
        if align == "center":
            return content.center(width)
        elif align == "right":
            return content.rjust(width)
        return content.ljust(width)

    def format_section(title, ingredients_list):
        rows = []
        for ing in filter(None, ingredients_list):
            total_weight = round(
                ing["servings"] * ing["serving"] * ing["conversion"] * 100)
            row = [
                pad_cell(ing["name"], col_widths[0], "left"),
                pad_cell(ing["servings"], col_widths[1], "center"),
                pad_cell(format_serving(
                    ing["serving"], ing["units"]), col_widths[2], "center"),
                pad_cell(f"{total_weight} g", col_widths[3], "right"),
            ]
            rows.append("".join(row))

        # Header
        headers = [
            pad_cell("Ingredient", col_widths[0], "left"),
            pad_cell("Servings", col_widths[1], "center"),
            pad_cell("Serving Size", col_widths[2], "center"),
            pad_cell("Total Weight", col_widths[3], "right"),
        ]
        header_line = "".join(headers)
        underline = "-" * DEFAULT_WIDTH

        section_title = subtitle(title, top=False)
        return section_title + "\n" + header_line + "\n" + underline + "\n" + "\n".join(rows)


    exclusions = [str(x) for x in data["exclusions"]]
    line = f"{', '.join(exclusions[:-1])} and {exclusions[-1]}"
    wrapped = "\n".join(wrap(line, DEFAULT_WIDTH))
    summary = [
        pad_between(f"Total Energy: ", f" {energy_kj:.2f} kJ ({energy_cal:.2f} cal)"),
        pad_between(f"Daily Energy: ", f" {daily_energy:.2f} kJ ({daily_energy / 4.184:.2f} cal)"),
        pad_between(f"Total Protein: ", f" {data['protein']['total']:.2f} g ({daily_protein:.2f} g/day)"),
        pad_between(f"Total Carbohydrates: ", f" {data['carbohydrate']:.2f} g"),
        format_section("Restricted Rations", data["protein"]["ingredients"] + data["non_protein"]),
        "\n" + subtitle("Unlimited Rations", top=False) + wrapped,
        hr()
    ]

    return "\n".join(summary)


def get_todays_rations_string(name, offset=0):
    year, week, _ = date.today().isocalendar()
    seed = int(f"{year}{week:02d}") + offset
    rng = random.Random(seed)
    return render_ingredients(get_ingredients(rng))
