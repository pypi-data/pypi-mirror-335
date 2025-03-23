import colorama


def print_string(text: str):
    """Prints the input text with each character in a different color.

    Args:
      text: The text to print.
    """

    colorama.init(strip=False)
    colors = [
        colorama.Fore.RED,
        colorama.Fore.GREEN,
        colorama.Fore.YELLOW,
        colorama.Fore.BLUE,
        colorama.Fore.MAGENTA,
        colorama.Fore.CYAN,
    ]
    print(len(text), "{", end="")
    for i, char in enumerate(text):
        print(colors[i % len(colors)] + repr(char)[1:-1], end="")
    print(colorama.Style.RESET_ALL, end="")
    print("}")
