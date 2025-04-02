import random
import json
from time import sleep
from datetime import date, timedelta
from colorama import Fore

from functions.helpers import random_ending
from functions.os import (
    loading_ellipsis,
    menu_prompt, typed_print, get_resource_path,
    typed_input, numeric_input, subtitle
)
from options import WORKOUT_CONSOLE_PREFIX, USER_PREFIX, DEFAULT_WIDTH

# Globals
NAME = None
STRENGTH_WORKOUTS = None
GROWTH_WORKOUTS = None
CARDIO_WORKOUTS = None

DAY = None
WEEK = None
MAX_WEIGHT = 160

def init_workout(name):
    global NAME, STRENGTH_WORKOUTS, GROWTH_WORKOUTS, CARDIO_WORKOUTS, DAY, WEEK
    NAME = name
    with open(get_resource_path("data/workout.json"), "r") as file:
        data = json.load(file)

    STRENGTH_WORKOUTS = data["strength"]
    GROWTH_WORKOUTS = data["growth"]
    CARDIO_WORKOUTS = data["cardio"]

    today = date.today()
    WEEK = today.isocalendar().week % 2
    DAY = today.strftime("%A")

def init(name):
    typed_print(f"{WORKOUT_CONSOLE_PREFIX}Initializing exercise server", newline=False)
    loading_ellipsis(length=1, sleep_for=0.3)
    init_workout(name)
    loading_ellipsis(length=2, sleep_for=0.3)
    print()
    typed_print(f"{WORKOUT_CONSOLE_PREFIX}Exercise server set up!")
    sleep(0.3)
    print()

def end_workout_string(name):
    prompt = random.choice([
        "Enjoy your workout!",
        "Have a great session!",
        "Push yourself to the limit!",
        "Stay strong and focused!",
        "Make every rep count!",
    ])
    return f"{prompt} {random_ending(name)}"

def calculate_cardio_output(cardio, weight):
    delta_weight = MAX_WEIGHT - weight
    if cardio["mode"] == "duration":
        duration = min(max(cardio["base"] + delta_weight * cardio["increment_per_unit"], cardio["min"]), cardio["max"])
        return f"{round(duration)} minutes"
    else:
        distance = min(max(cardio["base"] + delta_weight * cardio["increment_per_unit"], cardio["min"]), cardio["max"])
        return f"{round(distance, 2)} km"

def title_pad(string):
    return f"{subtitle("TODAY'S WORKOUT")}{string}"

def get_workout_string(name, weight, offset=0):
    global NAME, DAY, WEEK

    if not all([STRENGTH_WORKOUTS, GROWTH_WORKOUTS, CARDIO_WORKOUTS]):
        init_workout(name)

    target_date = date.today() + timedelta(days=offset)
    DAY = target_date.strftime("%A")
    WEEK = target_date.isocalendar().week % 2

    if DAY not in ["Monday", "Wednesday", "Friday"]:
        return title_pad(f"No workout scheduled for {DAY}.")

    day_shift = {"Monday": 0, "Wednesday": 1, "Friday": 2}[DAY]
    cycle = "A" if (WEEK + (1 if DAY != "Monday" else 0)) % 2 == 0 else "B"

    strengths = [w for w in STRENGTH_WORKOUTS if cycle in w["workouts"]]
    growths = GROWTH_WORKOUTS[2 * day_shift: 2 * day_shift + 2]
    cardio = CARDIO_WORKOUTS[day_shift]

    def pad_table(headers, rows, aligns=None, col_widths=None):
        if not col_widths:
            col_widths = [int(DEFAULT_WIDTH * p) for p in [0.6, 0.2, 0.2][:len(headers)]]
        if not aligns:
            aligns = ["left", "center", "right"][:len(headers)]

        def pad(text, width, align):
            text = str(text)
            if len(text) > width:
                return text[:width]
            if align == "center":
                return text.center(width)
            elif align == "right":
                return text.rjust(width)
            return text.ljust(width)

        header_line = "".join(pad(h, w, a) for h, w, a in zip(headers, col_widths, aligns))
        dashed = "-" * DEFAULT_WIDTH
        row_lines = ["".join(pad(cell, w, a) for cell, w, a in zip(row, col_widths, aligns)) for row in rows]
        return "\n".join([header_line, dashed] + row_lines)

    strength_rows = [[w["title"], f'{w["set"]}×{w["reps"]}'] for w in strengths]
    growth_rows = [[w["title"], f'{w["set"]}×{w["reps"]}', f'{w["restSeconds"]}s'] for w in growths]
    cardio_info = calculate_cardio_output(cardio, weight)

    strength_section = f"{subtitle('Strength', top=False)}\n{pad_table(['Exercise', 'Sets×Reps'], strength_rows)}"
    growth_section = f"{subtitle('Growth', top=False)}\n{pad_table(['Exercise', 'Sets×Reps', 'Rest'], growth_rows)}"
    cardio_section = f"{subtitle('Cardio', top=False)}\n{cardio['title']}: {cardio_info}"

    return title_pad(f"You have a workout scheduled for today {DAY}.\n{strength_section}\n{growth_section}\n{cardio_section}\n")

def get_workout():
    weight = numeric_input(f"{WORKOUT_CONSOLE_PREFIX}Enter your current weight\n{USER_PREFIX}")
    workout_str = get_workout_string(NAME, weight)
    typed_print(workout_str)

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
    mode = menu_prompt([
        {"title": "workout", "description": "Get today's workout"},
        {"title": "help", "description": "Learn the regiment"}
    ], title="option")

    if not mode:
        return

    if mode == "workout":
        weight = numeric_input(f"{WORKOUT_CONSOLE_PREFIX}Enter your current weight\n{USER_PREFIX}")
        workout = get_workout_string(name, weight)
        typed_print(workout)

    elif mode == "help":
        show_workout_help()

def run_workout_loop(name):
    init(name)
    while True:
        run_workout_prompt(name)

        typed_print(f"{WORKOUT_CONSOLE_PREFIX}Run another query? (y/n)")
        again = typed_input(f"{USER_PREFIX}").strip().lower()

        if again not in ("y", "yes"):
            print()
            typed_print(f"{WORKOUT_CONSOLE_PREFIX}Shutting down exercise server", newline=False)
            loading_ellipsis(length=3, sleep_for=0.5)
            print("\n")
            break

    return end_workout_string(name)
