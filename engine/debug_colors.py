from dataclasses import dataclass
import random
from termcolor import cprint, colored


@dataclass
class IColor:
    rgb: tuple[int, int, int]
    terminal_color: str

    def get_colored(self, text: any) -> str:
        return colored(text, self.terminal_color)

    def print(self, text: any) -> None:
        cprint(self.get_colored(text))


# See avilable terminal colors:
# https://github.com/termcolor/termcolor


class Red(IColor):
    def __init__(self):
        super().__init__((255, 0, 0), "red")


class Green(IColor):
    def __init__(self):
        super().__init__((0, 255, 0), "green")


class Yellow(IColor):
    def __init__(self):
        super().__init__((255, 255, 0), "yellow")


class Blue(IColor):
    def __init__(self):
        super().__init__((0, 0, 255), "blue")


class Magenta(IColor):
    def __init__(self):
        super().__init__((255, 0, 255), "magenta")


class Cyan(IColor):
    def __init__(self):
        super().__init__((0, 255, 255), "cyan")


class Colors:
    _ALL_COLORS = [Red(), Green(), Yellow(), Blue(), Magenta(), Cyan()]

    @staticmethod
    def get_random_color():
        return Colors._ALL_COLORS[random.randint(0, len(Colors._ALL_COLORS) - 1)]

    @staticmethod
    def get_all_colors():
        return Colors._ALL_COLORS.copy()


if __name__ == "__main__":
    for color in Colors._ALL_COLORS:
        print(color.get_colored("Hello World!"))
        color.print("Hello World!")
        print()
