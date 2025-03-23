#!/usr/bin/env python

import logging
import os
import pty
import select
import subprocess
import threading
import time

import click
import colorama

log = logging.getLogger(__name__)


@click.command()
def cli():
    log.info("started")
    master, slave = pty.openpty()
    subprocess.Popen(["bash"], stdin=slave, stdout=slave, stderr=slave)

    def read_output():
        log.info("started reading output")
        while True:
            ravailables, _, _ = select.select([master], [], [], 1)
            if ravailables:
                output = os.read(master, 1024)
                print(output.decode("utf8"), end="")
                time.sleep(0.1)

    threading.Thread(target=read_output).start()

    while True:
        next_cmd = input(colorama.Fore.GREEN + "Enter command: " + colorama.Fore.RESET)
        if next_cmd == "quit!":
            break
        os.write(master, bytes(next_cmd + "\n", "utf8"))


if __name__ == "__main__":
    loglevel = "DEBUG"
    try:
        import coloredlogs

        coloredlogs.install(level=loglevel)
    except ImportError:
        logging.basicConfig(level=loglevel)
    logging.root.setLevel("INFO")
    log.setLevel(loglevel)
    cli()
