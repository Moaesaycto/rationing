from time import sleep
import random
import json
from itertools import chain
from colorama import Fore
from tabulate import tabulate

from functions.helpers import random_ending
from functions.os import (
    get_resource_path,
    numeric_input,
    render_progress_bar,
    typed_print,
    loading_ellipsis
)
from options import HEALTH_CONSOLE_PREFIX, USER_PREFIX

# Globals
SUPPLEMENTS = []
NOTES = []
STATS = {}
WEIGHT = 160
NAME = ""


def run_health(name):
    global SUPPLEMENTS, NOTES, STATS, NAME, WEIGHT

    NAME = name

    typed_print(
        f"{HEALTH_CONSOLE_PREFIX}Initializing health program", newline=False)

    with open(get_resource_path("data/health.json")) as file:
        data = json.load(file)
        SUPPLEMENTS = data["supplements"]
        NOTES = data["notes"]
        STATS = data["stats"]

    loading_ellipsis()
    print()
    typed_print(f"{HEALTH_CONSOLE_PREFIX}Health program loaded!\n")

    WEIGHT = numeric_input(
        f"{HEALTH_CONSOLE_PREFIX}Enter your current weight\n{USER_PREFIX}")

    print()
    sleep(0.3)
    typed_print(
        f"{HEALTH_CONSOLE_PREFIX}Generating health report", newline=False)
    loading_ellipsis(sleep_for=0.5)
    print()

    report = "\n".join([
        get_supplements(),
        get_progress(),
        get_notes()
    ])

    typed_print(
        f"{HEALTH_CONSOLE_PREFIX}Successfully generated report:", newline=False)
    typed_print(report)
    print()

    return random.choice([
        f"Be well, {NAME}.",
        f"Stay healthy, {NAME}!",
        f"Take care of yourself, {NAME}.",
        f"Keep up the great work, {NAME}!",
        f"You're doing amazing, {NAME}.",
        f"Health is wealth, {NAME}.",
        f"Stay strong, {NAME}!",
        f"Keep pushing forward, {NAME}.",
        f"You're on the right track, {NAME}.",
        f"Every step counts, {NAME}.",
        f"Remember to rest, {NAME}.",
        f"Consistency is key, {NAME}.",
        f"You're unstoppable, {NAME}!",
        f"Keep striving for greatness, {NAME}.",
        f"Your health journey is inspiring, {NAME}.",
        f"Stay motivated, {NAME}!",
        f"You're making progress, {NAME}.",
        f"Believe in yourself, {NAME}.",
        f"Your efforts matter, {NAME}.",
        f"Keep your goals in sight, {NAME}."
    ]) + " " + random_ending(NAME)


def get_supplements():
    table = [[f"{Fore.RESET}{s['title']}", s["dose"], s["time"]]
             for s in SUPPLEMENTS]
    section = Fore.CYAN + "\n--- SUPPLEMENTS ---\n" + Fore.RESET
    section += tabulate(table, headers=[f"{Fore.CYAN}Title", "Dose", "Time"])

    micros = sorted(set(chain.from_iterable(
        s["nutrients"] for s in SUPPLEMENTS)))
    section += f"\n{Fore.CYAN}Micros:{Fore.RESET} " + ", ".join(micros)

    return section


def get_progress():
    title = Fore.YELLOW + "\n--- PROGRESS ---" + Fore.RESET
    start = STATS["starting_weight"]
    goal = STATS["goal_weight"]
    lost = start - WEIGHT
    target = start - goal
    bar = render_progress_bar(lost, target)

    return "\n".join([
        title,
        f"{Fore.YELLOW}Starting Weight:{Fore.RESET} {start}kg",
        f"{Fore.YELLOW}Current Weight:{Fore.RESET} {WEIGHT}kg",
        f"{Fore.YELLOW}Total Lost:{Fore.RESET} {lost}kg out of {target}kg",
        f"{Fore.YELLOW}Progress:{Fore.RESET} {bar}"
    ])


def get_notes():
    section = Fore.MAGENTA + "\n--- NOTES ---\n" + Fore.RESET
    return section + "\n".join(
        [f"{Fore.MAGENTA}{n['title']}:{Fore.RESET} {n['description']}" for n in NOTES]
    )
