from textwrap import wrap
from time import sleep
import random
import json
from itertools import chain

from functions.helpers import random_ending
from functions.os import (
    get_resource_path,
    numeric_input,
    pad_between,
    render_progress_bar,
    subtitle,
    typed_print,
    loading_ellipsis
)
from options import HEALTH_CONSOLE_PREFIX, USER_PREFIX, DEFAULT_WIDTH

# Globals
SUPPLEMENTS = []
NOTES = []
STATS = {}
NAME = ""


def init_health(name):
    global SUPPLEMENTS, NOTES, STATS, NAME
    NAME = name
    with open(get_resource_path("data/health.json")) as file:
        data = json.load(file)
        SUPPLEMENTS = data["supplements"]
        NOTES = data["notes"]
        STATS = data["stats"]


def run_health(name):
    global NAME
    NAME = name

    typed_print(
        f"{HEALTH_CONSOLE_PREFIX}Initializing health program", newline=False)
    init_health(name)
    loading_ellipsis()
    print()
    typed_print(f"{HEALTH_CONSOLE_PREFIX}Health program loaded!\n")

    weight = numeric_input(
        f"{HEALTH_CONSOLE_PREFIX}Enter your current weight\n{USER_PREFIX}")

    print()
    sleep(0.3)
    typed_print(
        f"{HEALTH_CONSOLE_PREFIX}Generating health report", newline=False)
    loading_ellipsis(sleep_for=0.5)
    print()

    report = get_health_report(name, weight)
    typed_print(
        f"{HEALTH_CONSOLE_PREFIX}Successfully generated report:")
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


def pad_table(headers, rows, aligns=None, col_widths=None):
    if not col_widths:
        col_widths = [int(DEFAULT_WIDTH * p)
                      for p in [0.5, 0.25, 0.25][:len(headers)]]
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

    header_line = "".join(pad(h, w, a)
                          for h, w, a in zip(headers, col_widths, aligns))
    dashed = "-" * DEFAULT_WIDTH
    row_lines = ["".join(pad(cell, w, a) for cell, w, a in zip(
        row, col_widths, aligns)) for row in rows]
    return "\n".join([header_line, dashed] + row_lines)


def get_health_report(name, weight):
    if not all([SUPPLEMENTS, NOTES, STATS]):
        init_health(name)

    return "\n".join([
        get_supplements_section(),
        get_progress_section(weight),
        get_notes_section()
    ])


def get_supplements_section():
    table = [[s['title'], s["dose"], s["time"]] for s in SUPPLEMENTS]
    header = subtitle("HEALTH REPORT")
    description = "Below is a list of required daily supplements along with dietary notes and progress towards you goal"
    wrapped_description = "\n".join(wrap(description, width=DEFAULT_WIDTH))
    rendered_table = pad_table(["Title", "Dose", "Time"], table, aligns=[
                               "left", "center", "right"])
    micros = sorted(set(chain.from_iterable(
        s["nutrients"] for s in SUPPLEMENTS)))
    micros_line = ", ".join(micros)
    wrapped_micros = wrap(micros_line, width=DEFAULT_WIDTH - len("Micros: "))

    wrapped_micros[0] = f"Micros: {wrapped_micros[0]}"
    for i in range(1, len(wrapped_micros)):
        wrapped_micros[i] = f"{' ' * len('Micros: ')}{wrapped_micros[i]}"

    micros_block = "\n".join(wrapped_micros)
    return "\n".join([
        header,
        wrapped_description,
        subtitle("Supplements", top=False),
        rendered_table,
        "\n",
        micros_block
    ])


def get_progress_section(weight):
    init_health(NAME)
    start = STATS["starting_weight"]
    goal = STATS["goal_weight"]
    lost = start - weight
    target = start - goal
    bar = render_progress_bar(
        lost, target, DEFAULT_WIDTH - len("Progress: [] 66% "))

    lines = [
        pad_between("Starting Weight: ", f" {start}kg"),
        pad_between("Current Weight: ", f" {weight}kg"),
        pad_between("Total Lost:", f" {lost}kg out of {target}kg\n"),
        f"Progress: {bar}\n"
    ]
    return f"{subtitle("Progress", top=False)}\n" + "\n".join(lines)


def get_notes_section():
    note_lines = ["\n".join(wrap(f"{n['title']}: {n['description']}", width=DEFAULT_WIDTH)) for n in NOTES]
    return f"{subtitle("Additional Notes", top=False)}\n" + "\n".join(note_lines)
