#!/usr/bin/env python3
import logging
import os
import sys
from functools import cached_property
from pathlib import Path
from shutil import which
from typing import Dict, Optional

import click
from attrs import asdict, define, field

from dbox.logging.colored import setup_colored_logging
from dbox.shellx import fire

log = logging.getLogger(__name__)
parent_dir = Path(__file__).parent


def to_path(path) -> Path:
    if path is None:
        return None
    if isinstance(path, Path):
        return path
    return Path(path)


@define(kw_only=True)
class TfConfig:
    terraform_bin: Optional[Path] = field(default=None, converter=to_path)
    workspace: Optional[Path] = field(default=Path.cwd(), converter=to_path)
    data_dir: Optional[Path] = field(default=Path(".terraform"), converter=to_path)
    var_file: Optional[Path] = field(default=None, converter=to_path)
    backend_config: Optional[Path] = field(default=None, converter=to_path)


class TfCommand:
    def __init__(self, config: TfConfig):
        self.config = config

    @property
    def workspace(self) -> Path:
        return self.config.workspace

    def terrafire(self, command, *args, **kwargs):
        cmd = (self.config.terraform_bin.as_posix(), "-chdir={}".format(self.workspace.as_posix()), command, *args)
        command_env = {**os.environ, "TF_DATA_DIR": self.config.data_dir.as_posix()}
        log.info("Running: %s", " ".join(cmd))
        try:
            fire(*cmd, popen_kwargs={"env": command_env, "cwd": self.workspace}, **kwargs)
        except Exception as e:
            log.error("Command failed: %s", e)
            sys.exit(1)

    def init(self, *tf_arguments):
        cmds = ["init"]
        if self.config.backend_config:
            cmds.extend(["--backend-config", self.config.backend_config.as_posix()])
        cmds.extend(tf_arguments)
        self.terrafire(*cmds)

    def _run(self, command, *tf_arguments):
        cmds = [command]
        if self.config.var_file:
            cmds.extend(["-var-file", self.config.var_file.as_posix()])
        cmds.extend(tf_arguments)
        self.terrafire(*cmds)

    def plan(self, *tf_arguments):
        self._run("plan", *tf_arguments)

    def apply(self, *tf_arguments):
        self._run("apply", *tf_arguments)

    def destroy(self, *tf_arguments):
        self._run("destroy", *tf_arguments)

    def import_resource(self, *tf_arguments):
        self._run("import", *tf_arguments)

    def show(self, *tf_arguments):
        self.terrafire("show", *tf_arguments)

    def output(self, *tf_arguments):
        self.terrafire("output", *tf_arguments)

    def fmt(self, *tf_arguments):
        fire(self.config.terraform_bin.as_posix(), "fmt", *tf_arguments)

    def force_unlock(self, *tf_arguments):
        self.terrafire("force-unlock", *tf_arguments)

    def generic(self, *tf_arguments):
        self.terrafire(*tf_arguments)


@click.group()
@click.pass_context
def cli(ctx: click.Context):
    import yaml

    tfpy = os.getenv("TFPY", ".tfpy.yaml")
    config_path = Path.cwd() / tfpy
    if not config_path.exists():
        log.error("Config file not found. Try to create .tfpy.yaml or set TFPY env variable.")
        log.info("Example config:")
        with (parent_dir / ".tfpy.sample.yaml").open("r") as f:
            print(f.read())
        sys.exit(1)

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    # render the config
    config = TfConfig(**config)
    config.terraform_bin = config.terraform_bin or Path(which("terraform"))
    config.workspace = config.workspace.absolute()
    config.data_dir = config.workspace / config.data_dir
    if config.var_file:
        config.var_file = config.workspace / config.var_file
    log.warning("Using config:")
    for k, v in asdict(config).items():
        print(f"  {k:<15}:  {v}")
    print()
    tf = TfCommand(config=config)
    ctx.obj = {}
    ctx.obj["tf"] = tf


@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument("tf_arguments", nargs=-1)
@click.pass_context
def init(ctx, tf_arguments):
    tf: TfCommand = ctx.obj["tf"]
    tf.init(*tf_arguments)


@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument("tf_arguments", nargs=-1)
@click.pass_context
def plan(ctx, tf_arguments):
    tf: TfCommand = ctx.obj["tf"]
    tf.plan(*tf_arguments)


@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument("tf_arguments", nargs=-1)
@click.pass_context
def apply(ctx, tf_arguments):
    tf: TfCommand = ctx.obj["tf"]
    tf.apply(*tf_arguments)


@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument("tf_arguments", nargs=-1)
@click.pass_context
def destroy(ctx, tf_arguments):
    tf: TfCommand = ctx.obj["tf"]
    tf.destroy(*tf_arguments)


@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument("tf_arguments", nargs=-1)
@click.pass_context
def import_resource(ctx, tf_arguments):
    tf: TfCommand = ctx.obj["tf"]
    tf.import_resource(*tf_arguments)


@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument("tf_arguments", nargs=-1)
@click.pass_context
def show(ctx, tf_arguments):
    tf: TfCommand = ctx.obj["tf"]
    tf.show(*tf_arguments)


@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument("tf_arguments", nargs=-1)
@click.pass_context
def output(ctx, tf_arguments):
    tf: TfCommand = ctx.obj["tf"]
    tf.output(*tf_arguments)


@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument("tf_arguments", nargs=-1)
@click.pass_context
def fmt(ctx, tf_arguments):
    tf: TfCommand = ctx.obj["tf"]
    tf.fmt(*tf_arguments)


@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument("tf_arguments", nargs=-1)
@click.pass_context
def force_unlock(ctx, tf_arguments):
    tf: TfCommand = ctx.obj["tf"]
    tf.force_unlock(*tf_arguments)


@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument("tf_arguments", nargs=-1)
@click.pass_context
def generic(ctx, tf_arguments):
    tf: TfCommand = ctx.obj["tf"]
    tf.generic(*tf_arguments)


if __name__ == "__main__":
    setup_colored_logging()
    # logging.getLogger("dbox.shellx").setLevel(logging.DEBUG)
    cli()
