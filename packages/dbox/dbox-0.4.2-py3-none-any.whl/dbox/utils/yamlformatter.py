import logging
from pathlib import Path

import click
import ruamel.yaml

from dbox.logging.colored import setup_colored_logging

yaml = ruamel.yaml.YAML()
yaml.indent(sequence=4, offset=2)
yaml.preserve_quotes = False
log = logging.getLogger(__name__)


@click.command()
@click.option("--file", "-f", required=True, help="YAML file to load and dump.")
@click.option("--inplace", "-i", is_flag=True, default=True, help="Edit file in place.")
def cli(file, inplace: bool):
    p = Path(file)
    if p.is_dir():
        paths = p.glob("**/*.yaml")
    else:
        paths = [p]
    for path in paths:
        log.info("Handling %s", path)
        with open(path) as f:
            data = yaml.load(f)
        if inplace:
            with open(path, "w") as f:
                yaml.dump(data, f)
        else:
            yaml.dump(data, click.get_text_stream("stdout"))


if __name__ == "__main__":
    setup_colored_logging()
    cli()
