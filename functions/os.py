import os
import sys
import time
import threading
import re
from colorama import Fore
from options import DEFAULT_WIDTH, TYPING_DELAY, ANSI_ESCAPE_PATTERN, TITLE_PADDING, TITLE_BORDER, TITLE_DELIMITER
from textwrap import wrap

# ----------------------------- #
#         GLOBAL CONFIG         #
# ----------------------------- #

skip_typing = False
listen_for_skip = False

# ----------------------------- #
#      KEY DETECTION LOGIC      #
# ----------------------------- #

if os.name == 'nt':
    import msvcrt

    def is_enter_pressed():
        return msvcrt.kbhit() and msvcrt.getch() == b'\r'

    def drain_input_buffer():
        while msvcrt.kbhit():
            msvcrt.getch()

else:
    import select
    import termios
    import tty

    def is_enter_pressed():
        dr, _, _ = select.select([sys.stdin], [], [], 0)
        return dr and sys.stdin.read(1) == '\n'

    def drain_input_buffer():
        # Set terminal to non-blocking raw mode, drain leftover chars
        try:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            tty.setcbreak(fd)
            while select.select([sys.stdin], [], [], 0)[0]:
                os.read(fd, 1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def start_skip_listener():
    def key_listener():
        global skip_typing, listen_for_skip
        while True:
            if listen_for_skip and is_enter_pressed():
                skip_typing = True
            time.sleep(0.01)

    threading.Thread(target=key_listener, daemon=True).start()


start_skip_listener()

# ----------------------------- #
#         PRINTING UTILS        #
# ----------------------------- #


def typed_print(text, delay=TYPING_DELAY, newline=True, skippable=True):
    if not text:
        return
    global skip_typing, listen_for_skip
    skip_typing = False
    listen_for_skip = skippable

    segments = ANSI_ESCAPE_PATTERN.split(text)
    current_style = ''
    skipping = False
    i = 0

    while i < len(segments):
        segment = segments[i]
        if ANSI_ESCAPE_PATTERN.fullmatch(segment):
            current_style = segment
            if not skipping:
                sys.stdout.write(segment)
                sys.stdout.flush()
            i += 1
            continue

        for j, char in enumerate(segment):
            if skippable and skip_typing:
                skipping = True
                sys.stdout.write(current_style + segment[j:])
                sys.stdout.flush()
                break
            sys.stdout.write(current_style + char)
            sys.stdout.flush()
            time.sleep(delay)

        if skipping:
            for k in range(i + 1, len(segments)):
                segment = segments[k]
                if ANSI_ESCAPE_PATTERN.fullmatch(segment):
                    current_style = segment
                    sys.stdout.write(current_style)
                else:
                    sys.stdout.write(current_style + segment)
            break

        i += 1

    if newline:
        print()

    listen_for_skip = False
    skip_typing = False
    if skippable:
        drain_input_buffer()


def typed_input(prompt='', delay=TYPING_DELAY, skippable=True):
    typed_print(prompt, delay=delay, newline=False, skippable=skippable)
    return input()


def loading_ellipsis(length=3, sleep_for=0.333, color=""):
    for _ in range(length):
        time.sleep(sleep_for)
        typed_print(color + ".", newline=False, skippable=False)


def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

# ----------------------------- #
#         INPUT HELPERS         #
# ----------------------------- #


def is_valid_number(s):
    s = re.sub(r'[^0-9.]', '', s).rstrip('.')
    return s and s != '.' and s.count('.') <= 1 and float(s) >= 0


def extract_number(s):
    s = re.sub(r'[^0-9.]', '', s).rstrip('.')
    try:
        return float(s) if s and s != '.' and s.count('.') <= 1 else None
    except ValueError:
        return None


def numeric_input(prompt):
    while not is_valid_number(value := typed_input(prompt)):
        continue
    return extract_number(value)


def menu_prompt(options, title="option", mode="text", return_key="title"):
    prompt = f"{Fore.MAGENTA}RC Console:{Fore.RESET} Choose {title}:\n"
    options = sorted(options, key=lambda x: x["title"].lower())
    option_map = {}

    if mode == "text":
        max_length = max(len(opt["title"]) for opt in options)
        for opt in options:
            name = opt["title"].lower()
            desc = opt.get("description", "")
            prompt += f" - {name.ljust(max_length + 1)}"
            prompt += f"| {desc}\n" if desc else "\n"
            option_map[name] = opt
        exit_label = "exit".ljust(max_length + 1)
    elif mode == "index":
        for i, opt in enumerate(options):
            prompt += f" - {i + 1}. {opt['title']}\n"
        option_map = {str(i + 1): opt for i, opt in enumerate(options)}
        exit_label = "exit "
    else:
        raise ValueError("Invalid mode. Use 'text' or 'index'.")

    prompt += f" - {exit_label}| Return to main CIQ console\n"
    prompt += f"{Fore.GREEN}You: {Fore.RESET}"

    while True:
        choice = typed_input(prompt).strip().lower()
        print()
        if choice == "exit":
            return None
        if choice in option_map:
            return option_map[choice].get(return_key, option_map[choice])
        typed_print(
            f"{Fore.RED}Invalid choice.{Fore.RESET} Please try again.\n")
        time.sleep(0.5)

# ----------------------------- #
#     RESOURCE PATH HANDLER     #
# ----------------------------- #


def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


# -------------------------- #
#      STRING RENDERERS      #
# -------------------------- #

def render_progress_bar(
    progress,
    total,
    length=30,
    filled_char="█",
    partial_chars="▓▒░",  # "▉▊▋▌▍▎▏",
    empty_char="░",
    show_percent=True,
    prefix="",
    suffix=""
):
    if total <= 0:
        raise ValueError("Total must be greater than 0")
    progress = max(0, min(progress, total))
    ratio = progress / total
    full_blocks = int(length * ratio)
    partial_index = int((length * ratio - full_blocks) * len(partial_chars))
    bar = filled_char * full_blocks + (partial_chars[partial_index - 1] if 0 < partial_index < len(
        partial_chars) else "") + empty_char * (length - full_blocks - (1 if 0 < partial_index < len(partial_chars) else 0))
    return f"{prefix}[{bar}]{f' {int(ratio * 100)}%' if show_percent else ''}{suffix}"


def create_title(string, width=None):
    secs = wrap(string, width) if width else string.split("\n")

    px, py = TITLE_PADDING
    bx, by = TITLE_BORDER
    d = TITLE_DELIMITER

    g = width if width else len(max(secs, key=len)) + 2 * px
    n = g + 2 * bx * len(d)

    tb = [d * n] * by + [f"{' ' * g}".join([d * bx] * 2)] * py
    body = [f"{d * bx}{s.center(g)}{d * bx}" for s in secs]

    return "\n".join(tb + body + tb[::-1])


def pad_between(left, right, width=DEFAULT_WIDTH, delim="."):
    pad_len = max(0, width - len(left) - len(right))
    return f"{left}{delim * pad_len}{right}"


def subtitle(string, width=DEFAULT_WIDTH, delim="_", top=True):
    return (hr(new_line=False, width=width) + "\n" if top else "") + f" {string} ".center(width, delim) + "\n"


def hr(new_line=True, width=DEFAULT_WIDTH):
    return f"{"_"*width}" + ("\n" if new_line else "")
