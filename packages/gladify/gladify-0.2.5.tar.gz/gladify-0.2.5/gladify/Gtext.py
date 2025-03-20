class Gtext:
    fg_code = {
        "black": "\033[30m", "red": "\033[31m", "green": "\033[32m", "yellow": "\033[33m",
        "blue": "\033[34m", "magenta": "\033[35m", "cyan": "\033[36m", "white": "\033[37m",
        "gray": "\033[90m", "light_red": "\033[91m", "light_green": "\033[92m", "light_yellow": "\033[93m",
        "light_blue": "\033[94m", "light_magenta": "\033[95m", "light_cyan": "\033[96m", "light_white": "\033[97m"
    }

    bg_code = {
        "black": "\033[40m", "red": "\033[41m", "green": "\033[42m", "yellow": "\033[43m",
        "blue": "\033[44m", "magenta": "\033[45m", "cyan": "\033[46m", "white": "\033[47m",
        "gray": "\033[100m", "light_red": "\033[101m", "light_green": "\033[102m", "light_yellow": "\033[103m",
        "light_blue": "\033[104m", "light_magenta": "\033[105m", "light_cyan": "\033[106m", "light_white": "\033[107m"
    }

    format_code = {
        "bold": "\033[1m", "dim": "\033[2m", "italic": "\033[3m", "underline": "\033[4m",
        "blink": "\033[5m", "reverse": "\033[7m", "hidden": "\033[8m"
    }

    def __init__(self):
        self.result = None

    def out(self, string=""):
        print(f"{string}{self.result}")
        return self

    def outStyle(self, text, fg=None, bg=None, design=None):
        style = []

        if fg:
            fg = fg.lower()
            if fg in self.fg_code:
                style.append(self.fg_code[fg])
            else:
                raise ValueError(f"Invalid foreground color '{fg}'.")

        if bg:
            bg = bg.lower()
            if bg in self.bg_code:
                style.append(self.bg_code[bg])
            else:
                raise ValueError(f"Invalid background color '{bg}'.")

        if design:
            if not isinstance(design, tuple):  # Ensure design is a tuple
                raise ValueError("Design must be a tuple, e.g., ('bold', 'italic').")
            for d in design:
                d = d.lower()
                if d in self.format_code:
                    style.append(self.format_code[d])
                elif d in ["b", "u"]:  # Allow 'b' for bold and 'u' for underline
                    style.append(self.format_code["bold"] if d == "b" else self.format_code["underline"])
                else:
                    raise ValueError(f"Invalid text format '{d}'.")

        self.result = f"{''.join(style)}{text}\033[0m"
        return self