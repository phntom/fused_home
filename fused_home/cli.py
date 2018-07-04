# -*- coding: utf-8 -*-

"""Console script for fused_home."""
import sys
import click


@click.command()
def main(args=None):
    """Console script for fused_home."""
    click.echo("Welcome to Fused Home")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
