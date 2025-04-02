from datetime import datetime
from time import sleep
from colorama import init, Fore, Style

from options import MAIN_CONSOLE_PREFIX, MAIN_CONSOLE_PREFIX_WARN, USER_PREFIX
from functions.commands import get_best_command, execute_command, init_commands
from functions.fun import ageis_welcome, random_sid
from functions.auth import auth, get_creds
from functions.os import clear_console, loading_ellipsis, typed_input, typed_print

init(autoreset=True)

NAME = None
SID = None


def on_begin():
    typed_print(
        f"{Fore.GREEN}Establishing connection to host terminal", newline=False)
    loading_ellipsis(color=Fore.GREEN)
    sleep(0.5)
    print()

    name_attempt = typed_input(f"{Fore.CYAN}Enter identifying credential: ")
    sleep(0.5)

    typed_print("Verifying credentials", newline=False, skippable=False)
    loading_ellipsis(sleep_for=0.1)
    sleep(0.3)
    print()

    if not auth(name_attempt):
        typed_print(
            f"{Style.BRIGHT}{Fore.RED}Invalid Credentials", skippable=False)
        typed_print(
            f"{Fore.RED}Disconnecting from host: {Fore.YELLOW}Error 403 (Forbidden)",
            newline=False, skippable=False
        )
        return

    creds = get_creds(name_attempt)
    global NAME, SID
    NAME = creds["name"]
    SID = random_sid()

    print()
    typed_print(f"{Fore.GREEN}Welcome, {NAME}!", skippable=True)
    typed_print("You will be redirected shortly",
                newline=False, skippable=True)
    loading_ellipsis(sleep_for=0.5)
    sleep(1)

    clear_console()
    ageis_welcome()

    typed_print(
        f"{Fore.CYAN}Initializing session for: {Fore.RESET}{creds['identifier']}")
    typed_print(
        f"{Fore.CYAN}Local time: {Fore.RESET}{datetime.now().isoformat()}")
    typed_print(f"{Fore.CYAN}SID: {Fore.RESET}{SID}")
    typed_print(f"{Fore.CYAN}Authorization: {Fore.RESET}FBAKARR (Proxy): Clearance Level 0")
    print()
    sleep(1)

    typed_print(
        f"{MAIN_CONSOLE_PREFIX}Hello, {NAME}! How can I be of assistance?")
    init_commands(NAME, SID)

    run_command_loop()


def run_command_loop():
    while True:
        user_input = typed_input(f"{USER_PREFIX}")
        loading_ellipsis(sleep_for=0.5, color=Fore.BLUE)
        print()

        keep_open, response = parse_input(user_input)
        prefix = MAIN_CONSOLE_PREFIX if keep_open else MAIN_CONSOLE_PREFIX_WARN
        typed_print(f"{prefix}{response}")

        if not keep_open:
            break


def parse_input(command):
    best_command = get_best_command(command)
    return execute_command(best_command)
