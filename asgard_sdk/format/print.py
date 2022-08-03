from sys import exit
from colorama import Fore, Style

RED = Fore.RED
GREEN = Fore.GREEN
BLUE = Fore.BLUE

NC = Style.RESET_ALL

def print_error(*text, fatal=False):
    str = "[{r}error{nc}] ".format(r=RED, nc=NC)

    for t in text:
        str += t

    print(str)

    if fatal:
        exit(1)

def print_success(*text, fatal=False):
    str = "[{g}good{nc}] ".format(g=GREEN, nc=NC)

    for t in text:
        str += t

    print(str)

def print_info(*text, fatal=False):
    str = "[{b}info{nc}] ".format(b=BLUE, nc=NC)

    for t in text:
        str += t

    print(str)    