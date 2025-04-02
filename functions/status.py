from options import OUTPUT_DIRECTORY_PATH, REPORT_FILE_NAME
from functions.os import get_resource_path
from datetime import datetime
import os

def create_title(string):
    title_len = len(max(string.split("\n"), key=len))
    return f"title length = {title_len}"

def generate_status():
    report = ""
    report += f"Report generated at: {str(datetime.now())}"
    
    print(create_title("Hello\nWorldybeings"))
    save_status_report(report)

def save_status_report(string):
    os.makedirs("output", exist_ok=True)
    with open(get_resource_path(f"{OUTPUT_DIRECTORY_PATH}/{REPORT_FILE_NAME}"), "w") as file:
        file.write(string)
    return True

if __name__ == "__main__":
    generate_status()