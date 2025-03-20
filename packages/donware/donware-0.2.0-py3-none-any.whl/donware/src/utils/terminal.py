from rich import print
import shutil


def banner(content: str, symbol: str = "-", text_position: str = "CENTER") -> None:
    """
    Print a banner to the terminal with the given content aligned and padded with the specified symbol.

    Parameters:
        content (str): text to be displayed in the banner.
        symbol (str): character used to pad the content to the terminal width. Default is '-'.
        text_position (str): alignment of the text within the banner. Can be 'CENTER', 'LEFT', or 'RIGHT'. Default is 'CENTER'.

    Example:
    >>> banner("hello world", text_position="CENTER")
        ---- hello world ----
    """

    match text_position:
        case "CENTER":
            terminal_width, _ = shutil.get_terminal_size()
            content = " " + content.strip() + " "
            content = content.center(terminal_width, symbol)
            print(content)
        case "LEFT":
            terminal_width, _ = shutil.get_terminal_size()
            content = " " + content.strip() + " "
            content = content.ljust(terminal_width, symbol)
            print(content)
        case "RIGHT":
            terminal_width, _ = shutil.get_terminal_size()
            content = " " + content.strip() + " "
            content = content.rjust(terminal_width, symbol)
            print(content)
        case _:
            raise ValueError(f">>> invalid text_position: {text_position}; choose from 'CENTER', 'LEFT', or 'RIGHT'.")
