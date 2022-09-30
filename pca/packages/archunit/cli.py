"""Console script for pca-archunit."""

import click


@click.command()
def main():
    """Run the main entrypoint."""
    click.echo("pca-archunit")
    click.echo("=" * len("pca-archunit"))
    click.echo("A DSL & testing library for your architecture. Part of the python-clean-architecture project.")


if __name__ == "__main__":
    main()  # pragma: no cover
