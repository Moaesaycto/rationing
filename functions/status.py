from functions.health import get_health_report
from functions.workout import get_workout_string
from functions.rations import get_todays_rations_string
from options import MAIN_CONSOLE_PREFIX, OUTPUT_DIRECTORY_PATH, REPORT_FILE_NAME, TITLE_BORDER, TITLE_PADDING, ANSI_ESCAPE_PATTERN, USER_PREFIX 
from functions.os import loading_ellipsis, create_title, hr, numeric_input, pad_between, subtitle, typed_print
from datetime import datetime, date
import os
from uuid import uuid4
import re
from functions.helpers import random_ending

TITLE_WIDTH = 78
TOTAL_WIDTH = TITLE_WIDTH + TITLE_BORDER[0] + TITLE_PADDING[0]

SPECS = [
    ["Report generated at: ", " " + str(datetime.now())],
    ["Authorized by: ", " F. BAKARR (Proxy)"],
    ["Report ID ", " " + str(uuid4())]
]

def generate_status(name):
    report = ""

    test_string = f"STATUS REPORT FOR: {date.today().strftime('%A, %B %d, %Y')}"
    report += create_title(test_string, width=TITLE_WIDTH) + "\n"
    report += subtitle("REPORT SPECIFICATIONS", width=TOTAL_WIDTH)
    report += "\n".join([pad_between(s[0], s[1], width=TOTAL_WIDTH, delim=".") for s in SPECS]) + "\n"
    report += hr(width=TOTAL_WIDTH) + "\n"
    report += subtitle("WEEKLY RATIONS", width=TOTAL_WIDTH)
    
    weight = numeric_input(f"{MAIN_CONSOLE_PREFIX}To get your report, please enter your current weight:\n{USER_PREFIX}")
    
    typed_print(f"{MAIN_CONSOLE_PREFIX}Generating your report now", newline=False)
    loading_ellipsis()
    print()
    
    report += ANSI_ESCAPE_PATTERN.sub('', get_todays_rations_string(name))
    report += "\n"*2
    report += ANSI_ESCAPE_PATTERN.sub('', get_workout_string(name, weight))
    report += "\n"*2
    report += ANSI_ESCAPE_PATTERN.sub('', get_health_report(name, weight))
    
    save_status_report(report)
    return "Report successfully generated! " + random_ending(name)


def save_status_report(string):
    output_dir = os.path.join(os.path.abspath("."), OUTPUT_DIRECTORY_PATH)
    os.makedirs(output_dir, exist_ok=True)

    file_path = os.path.join(output_dir, REPORT_FILE_NAME)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(string)

