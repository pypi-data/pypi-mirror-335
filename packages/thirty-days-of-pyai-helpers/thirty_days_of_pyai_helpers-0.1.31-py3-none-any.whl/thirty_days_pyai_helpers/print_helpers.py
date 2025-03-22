from colorama import init, deinit, Fore, Back, Style
import time

init(autoreset=True)

def slow_print(text, delay=0.1, newline=False):
    print(f"{newline and '\n'}{Fore.CYAN}{text}")
    time.sleep(delay)

def slow_print_header(text, delay=0.1):
    print(f"\n{Back.BLUE}{Fore.WHITE}{text}")
    time.sleep(delay)

def slow_print_error(text, delay=0.1):
    print(f"\n{Fore.RED}⛔️ {text}")
    time.sleep(delay)