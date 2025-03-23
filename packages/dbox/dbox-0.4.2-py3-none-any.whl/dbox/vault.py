import logging
import sys
from pathlib import Path
from typing import Optional

import click

from dbox.logging.colored import setup_colored_logging
from dbox.utils.http_client import SimpleHttpClient

log = logging.getLogger(__name__)


class VaultClient(SimpleHttpClient):
    def __init__(self, kv_mount: Optional[str] = "kv"):
        super().__init__(base_url="https://127.0.0.1:8200/v1/")
        self.session.headers["X-Vault-Token"] = self.get_token()
        self.session.verify = False
        self.kv_mount = kv_mount

    def get_token(self):
        token_path = Path("~/.vault-token").expanduser()
        if not token_path.exists():
            raise RuntimeError("Vault token not found")
        return token_path.read_text().strip()

    def kv_get(self, path: str):
        path = f"{self.kv_mount}/data/{path}"
        res_text = self.get(path).text
        return res_text

    def kv_put(self, path: str, data: dict):
        path = f"{self.kv_mount}/data/{path}"
        self.post(path, json=data)


@click.group()
@click.pass_context
def cli(ctx):
    vault = VaultClient(kv_mount="kv-mount")
    ctx.obj = {"vault": vault}


@cli.command()
@click.pass_context
@click.argument("path")
def get(ctx, path):
    vault: VaultClient = ctx.obj["vault"]
    res = vault.kv_get(path)
    print(res, file=sys.stdout)


@cli.command()
@click.pass_context
@click.argument("path")
def put(ctx, path):
    vault: VaultClient = ctx.obj["vault"]
    vault.delete(path)


if __name__ == "__main__":
    setup_colored_logging()
    logging.getLogger("luna").setLevel(logging.DEBUG)
    cli()
