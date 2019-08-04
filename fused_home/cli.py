# -*- coding: utf-8 -*-

"""Console script for fused_home."""
import sys
import click


@click.command()
def main(args=None):
    """Console script for fused_home."""
    click.echo("Welcome to Fused Home")
    return 0


def homepage():
    return "hello"


@click.command()
def web(debug=True, port=5000, host='127.0.0.1'):
    from apistar import App, Route
    routes = [
        Route('/', method='GET', handler=homepage),
    ]
    app = App(routes=routes)
    app.serve(host, port, debug=debug)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
