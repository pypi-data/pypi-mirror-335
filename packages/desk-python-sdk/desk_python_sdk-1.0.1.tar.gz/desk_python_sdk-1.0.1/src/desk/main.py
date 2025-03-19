"""Command-line interface."""

import click


@click.command()
@click.version_option()
def main() -> None:
    """Desk Python SDK."""


if __name__ == "__main__":
    main(prog_name="desk-python-sdk")  # pragma: no cover
