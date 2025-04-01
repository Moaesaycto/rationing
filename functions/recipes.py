import json
from time import sleep
from colorama import Fore

from functions.helpers import random_food_ending
from functions.os import get_resource_path, loading_ellipsis, menu_prompt, typed_input, typed_print
from options import RATIONS_CONSOLE_PREFIX, USER_PREFIX

# ----------------------------- #
#           OPTIONS             #
# ----------------------------- #

TYPE_OPTIONS = [
    {"title": "sauce", "description": "See a list of sauces"},
    {"title": "marinade", "description": "Get this current week's rations"}
]

MEAT_OPTIONS = [
    {"title": "pork"},
    {"title": "chicken"},
    {"title": "beef"}
]

SAUCES = None
MARINADES = None

# ----------------------------- #
#           MAIN LOOP           #
# ----------------------------- #


def run_recipe_loop(name):
    while True:
        load_recipes(name)

        typed_print(f"{RATIONS_CONSOLE_PREFIX}Load another recipe? (y/n)")
        again = typed_input(f"{USER_PREFIX}").strip().lower()

        if again not in ("y", "yes"):
            print()
            typed_print(
                f"{RATIONS_CONSOLE_PREFIX}Shutting down recipe module", newline=False)
            loading_ellipsis(length=3, sleep_for=0.5)
            print()
            break

    return random_food_ending(name)

# ----------------------------- #
#         LOAD RECIPES          #
# ----------------------------- #


def load_recipes(name):
    typed_print(
        f"{RATIONS_CONSOLE_PREFIX}Preparing recipe data", newline=False)
    loading_ellipsis(length=2, sleep_for=0.3)

    with open(get_resource_path("data/recipes.json"), "r") as file:
        data = json.load(file)

    global SAUCES, MARINADES
    SAUCES, MARINADES = data["sauces"], data["marinades"]

    loading_ellipsis(length=1, sleep_for=0.3)
    print()
    typed_print(f"{RATIONS_CONSOLE_PREFIX}Data successfully loaded!")

    choice = menu_prompt(TYPE_OPTIONS)
    if choice == "sauce":
        show_sauce_list()
    elif choice == "marinade":
        show_marinade_list()

    sleep(0.5)

# ----------------------------- #
#        DISPLAY LOGIC          #
# ----------------------------- #


def show_recipe_prompt(recipe, kind):
    if not recipe:
        typed_print(f"{RATIONS_CONSOLE_PREFIX}No {kind} found.")
        return

    typed_print(f"{RATIONS_CONSOLE_PREFIX}Ingredients for {recipe['title']}:")
    for ing in recipe["ingredients"]:
        typed_print(f" - {ing}")
    print()


def show_marinade_list():
    meat = menu_prompt(MEAT_OPTIONS, title="a meat")
    if not meat:
        return

    options = [r for r in MARINADES if r["category"] == meat]
    recipe_id = menu_prompt(
        options, title=f"a marinade for {meat}", mode="index", return_key="id")
    if not recipe_id:
        return

    recipe = next((r for r in MARINADES if r["id"] == recipe_id), None)
    show_recipe_prompt(recipe, "marinade")


def show_sauce_list():
    recipe_id = menu_prompt(SAUCES, title="a sauce",
                            mode="index", return_key="id")
    if not recipe_id:
        return

    recipe = next((r for r in SAUCES if r["id"] == recipe_id), None)
    show_recipe_prompt(recipe, "sauce")
