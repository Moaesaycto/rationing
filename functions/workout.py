import random
import json
from time import sleep
from colorama import Fore
from functions.helpers import random_ending
from functions.os import extract_number, is_valid_number, loading_ellipsis, menu_prompt, typed_print, get_resource_path, typed_input
from options import WORKOUT_CONSOLE_PREFIX, USER_PREFIX
from datetime import date
from tabulate import tabulate

NAME = None
STRENGTH_WORKOUTS = None
GROWTH_WORKOUTS = None
CARDIO_WORKOUTS = None

DAY = None
WEEK = None
WEIGHT = 160
MAX_WEIGHT = 160


def end_workout_string(name):
    prompt = random.choice([
        "Enjoy your workout!",
        "Have a great session!",
        "Push yourself to the limit!",
        "Stay strong and focused!",
        "Make every rep count!",
    ])
    return f"{prompt} {random_ending(name)}"


def get_workout():
    DAY = "Monday"
    if DAY not in ["Monday", "Wednesday", "Friday"]:
        typed_print("No workout scheduled for today...")
        return

    day_shift = {"Monday": 0, "Wednesday": 1, "Friday": 2}[DAY]
    cycle = "A" if (WEEK + (1 if DAY != "Monday" else 0)) % 2 == 0 else "B"

    strengths = [w for w in STRENGTH_WORKOUTS if cycle in w["workouts"]]
    growths = GROWTH_WORKOUTS[2 * day_shift: 2 * day_shift + 2]
    cardio = CARDIO_WORKOUTS[day_shift]

    # Render Strength
    strength_table = [
        [w["title"], f'{w["set"]}×{w["reps"]}'] for w in strengths]
    strength_section = Fore.CYAN + "\n--- STRENGTH ---\n" + Fore.RESET + \
        tabulate(strength_table, headers=["Exercise", "Sets×Reps"])

    # Render Growth
    growth_table = [
        [w["title"], f'{w["set"]}×{w["reps"]}', f'{w["restSeconds"]}s'] for w in growths]
    growth_section = Fore.MAGENTA + "\n--- GROWTH ---\n" + Fore.RESET + \
        tabulate(growth_table, headers=["Exercise", "Sets×Reps", "Rest"])

    # Render Cardio
    delta_weight = MAX_WEIGHT - WEIGHT
    if cardio["mode"] == "duration":
        duration = min(max(cardio["base"] + delta_weight *
                       cardio["increment_per_unit"], cardio["min"]), cardio["max"])
        cardio_info = f"{round(duration)} minutes"
    else:
        distance = min(max(cardio["base"] + delta_weight *
                       cardio["increment_per_unit"], cardio["min"]), cardio["max"])
        cardio_info = f"{round(distance, 2)} km"
    cardio_section = Fore.GREEN + "\n--- CARDIO ---\n" + \
        Fore.RESET + f"{cardio['title']}: {cardio_info}"

    # Combine all sections into a single string
    workout_summary = f"{strength_section}\n\n{growth_section}\n\n{cardio_section}\n"
    typed_print(workout_summary)


def show_workout_help():
    workouts = STRENGTH_WORKOUTS + GROWTH_WORKOUTS
    titles = [w["title"] for w in workouts]
    choice = menu_prompt(
        [{"title": t.title(), "description": "View details"} for t in titles],
        title="workout", mode="index")

    if not choice:
        return

    match = next((w for w in workouts if w["title"] == choice), None)
    if not match:
        typed_print("Workout not found.")
        return

    details = Fore.YELLOW + f"--- {match['title'].upper()} ---\n" + Fore.RESET
    details += f"Sets × Reps: {match['set']} × {match['reps']}\n"
    if "restSeconds" in match:
        details += f"Rest: {match['restSeconds']} seconds\n"
    if "start" in match:
        details += f"Starting Weight: {match['start']} kg\n"
    if "increment" in match:
        details += f"Progression: +{match['increment']} kg/session\n"
    typed_print(details)


def run_workout_prompt(name):
    global NAME
    NAME = name
    typed_print(
        f"{WORKOUT_CONSOLE_PREFIX}Initializing exercise server", newline=False)
    loading_ellipsis(length=1, sleep_for=0.3)
    with open(get_resource_path("data/workout.json"), "r") as file:
        data = json.load(file)

    global STRENGTH_WORKOUTS, GROWTH_WORKOUTS, CARDIO_WORKOUTS
    STRENGTH_WORKOUTS = data["strength"]
    GROWTH_WORKOUTS = data["growth"]
    CARDIO_WORKOUTS = data["cardio"]
    loading_ellipsis(length=1, sleep_for=0.3)

    global DAY, WEEK
    today = date.today()
    WEEK = today.isocalendar().week % 2
    DAY = today.strftime("%A")

    loading_ellipsis(length=1, sleep_for=0.3)
    print()
    typed_print(
        f"{WORKOUT_CONSOLE_PREFIX}Exercise server set up!")
    sleep(0.3)
    print()

    mode = menu_prompt([
        {"title": "workout", "description": "Get today's workout"},
        {"title": "help", "description": "Learn the regiment"}
    ], title="option")

    if not mode:
        return

    if mode == "workout":
        global WEIGHT
        while not is_valid_number(WEIGHT := typed_input(f"{WORKOUT_CONSOLE_PREFIX}Enter your current weight\n{USER_PREFIX}")):
            pass
        WEIGHT = extract_number(WEIGHT)
        get_workout()

    elif mode == "help":
        show_workout_help()


def run_workout_loop(name):
    while True:
        run_workout_prompt(name)

        typed_print(f"{WORKOUT_CONSOLE_PREFIX}Run another query? (y/n)")
        again = typed_input(f"{USER_PREFIX}").strip().lower()

        if again not in ("y", "yes"):
            print()
            typed_print(
                f"{WORKOUT_CONSOLE_PREFIX}Shutting down recipe module", newline=False)
            loading_ellipsis(length=3, sleep_for=0.5)
            print()
            break

    return end_workout_string(name)
