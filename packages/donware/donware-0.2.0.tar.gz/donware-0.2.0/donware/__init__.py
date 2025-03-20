#!/Users/donyin/miniconda3/bin/python

import donware
from rich import print
from rich.table import Table
from donware.src.utils.terminal import banner

__all__ = ["banner"]


def doc(func: callable = None):
    """
    Prints the docstring of a given function. If no function is provided, print the entire current package.
    Args:
        func (callable): The function whose docstring will be printed.
    """
    if func is None:
        [doc(function) for function in [getattr(donware, function) for function in __all__]]
    else:
        table = Table(title=f"Function: {func.__name__}")
        table.add_column("Attribute", style="cyan")
        table.add_column("Value", style="green")
        table.add_row("name", func.__name__)
        table.add_row("docstring", func.__doc__ or ">>> no docstring available")
        print(table)
