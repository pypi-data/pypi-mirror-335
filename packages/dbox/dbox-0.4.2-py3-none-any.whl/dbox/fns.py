import json
import logging

log = logging.getLogger(__name__)


def io_load_json(p):
    with open(p) as f:
        return json.load(f)


def show_frame(df):
    from rich.console import Console
    from rich.table import Table

    console = Console()

    table = Table(show_header=True, header_style="bold blue")
    for c in df.columns:
        table.add_column(c)
    for _, row in df.iterrows():
        table.add_row(*[str(e) for e in dict(row).values()])
    console.print(table)


def omit(d: dict, keys: list[str]) -> dict:
    return {k: v for k, v in d.items() if k not in keys}


def pick(d: dict, keys: list[str]) -> dict:
    return {k: v for k, v in d.items() if k in keys}
