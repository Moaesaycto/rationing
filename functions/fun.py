import random
from colorama import Fore
from options import LOGO_BORDER_COLOR, LOGO_TEXT_COLOR, TITLE_COLOR, ANSI_ESCAPE_PATTERN

# ----------------------------- #
#            LOGO              #
# ----------------------------- #

LOGO = f"""\
 {LOGO_BORDER_COLOR}.----------------. 
| .--------------. |
| |      {LOGO_TEXT_COLOR}__{LOGO_BORDER_COLOR}      | |{TITLE_COLOR}           _____ ______ _____  _____ {LOGO_BORDER_COLOR}
| |     {LOGO_TEXT_COLOR}/  \\{LOGO_BORDER_COLOR}     | |{TITLE_COLOR}     /\\   / ____|  ____|_   _|/ ____|{LOGO_BORDER_COLOR}
| |    {LOGO_TEXT_COLOR}/ /\\ \\{LOGO_BORDER_COLOR}    | |{TITLE_COLOR}    /  \\ | |  __| |__    | | | (___  {LOGO_BORDER_COLOR}
| |   {LOGO_TEXT_COLOR}/ ____ \\{LOGO_BORDER_COLOR}   | |{TITLE_COLOR}   / /\\ \\| | |_ |  __|   | |  \\___ \\ {LOGO_BORDER_COLOR}
| | {LOGO_TEXT_COLOR}_/ /    \\ \\_{LOGO_BORDER_COLOR} | |{TITLE_COLOR}  / ____ \\ |__| | |____ _| |_ ____) |{LOGO_BORDER_COLOR}
| |{LOGO_TEXT_COLOR}|____|  |____|{LOGO_BORDER_COLOR}| |{TITLE_COLOR} /_/    \\_\\_____|______|_____|_____/ {LOGO_BORDER_COLOR}
| |              | |
| '--------------' |
 '----------------'"""

# ----------------------------- #
#           HELPERS            #
# ----------------------------- #


def visible_length(line):
    """Calculate the length of a string excluding ANSI codes."""
    return len(ANSI_ESCAPE_PATTERN.sub('', line))


def ageis_welcome():
    """Print the styled welcome banner."""
    width = max(visible_length(line) for line in LOGO.splitlines())
    print(Fore.GREEN + "=" * width)
    print(LOGO)
    print(Fore.GREEN + "=" * width)


def random_sid():
    """Generate a random SID like 1234-5678-901234."""
    return '-'.join(''.join(str(random.randint(0, 9)) for _ in range(n)) for n in (4, 4, 6))
