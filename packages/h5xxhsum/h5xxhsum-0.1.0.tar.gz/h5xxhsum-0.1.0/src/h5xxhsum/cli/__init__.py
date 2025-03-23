# SPDX-FileCopyrightText: 2024-present S. Miccoli <stefano.miccoli@polimi.it>
#
# SPDX-License-Identifier: MIT
import re
import sys

import click
import h5py

from h5xxhsum import Walker, __version__

digestre = re.compile(r"([0-9a-f]{32})\s+(.+)\n")


@click.command()
@click.argument("h5", nargs=-1)
@click.option("--check", "-c", multiple=False, type=click.File("r"))
@click.option("--chunked/--no-chunked", default=False)
@click.version_option(version=__version__, prog_name="h5xxhsum")
def h5xxhsum(h5, check, chunked):  # noqa: C901, PLR0912
    if h5 and check:
        click.secho(
            "Cannot both verify and compute checksums",
            file=sys.stderr,
            fg="red",
        )
        sys.exit(2)
    if check:
        verified = to_be_verified = 0
        for i, line in enumerate(check, start=1):
            mo = digestre.fullmatch(line)
            if not mo:
                click.secho(
                    f"{check.name}: invalid line {i:d}, stop",
                    file=sys.stderr,
                    fg="red",
                )
                sys.exit(1)
            ref, pth = mo.groups()
            to_be_verified += 1
            try:
                msg = data_hash(pth, chunked)
            except FileNotFoundError:
                click.secho(f"{pth}: Missing", bold=True)
                continue
            except OSError as err:
                click.secho(f"{pth}: Error: {err}", bold=True)
                continue
            if msg == ref:
                click.echo(f"{pth}: OK")
                verified += 1
            else:
                click.secho(f"{pth}: FAIL", bold=True)
        sys.exit(0 if verified == to_be_verified else 1)
    else:
        for pth in h5:
            try:
                msg = data_hash(pth, chunked)
            except FileNotFoundError:
                click.secho(f"{pth}: not found", file=sys.stderr, fg="red")
            except OSError as err:
                click.secho(f"{pth}: {err}", file=sys.stderr, fg="red")
            else:
                click.echo(f"{msg}  {pth}")
        sys.exit(0)


def data_hash(pth, chunked):
    callback = Walker(chunked=chunked)
    with h5py.File(pth, "r") as h5:
        h5.visititems(callback)
    return callback.hexdigest
