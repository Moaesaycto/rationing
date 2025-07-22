from functions.story import on_begin
from functions.os import clear_console
import traceback
import sys

def main():
    clear_console()
    on_begin()

if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        if hasattr(sys, '_MEIPASS'):  # Only pause if bundled
            input("\nAn error occurred. Press Enter to close...")
