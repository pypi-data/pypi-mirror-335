import typer
from . import revcomp

cli = typer.Typer()


@cli.command(name="revcomp")
def revcomp_wrapper(input: str):
    print(revcomp(input))


@cli.command()
def upper(input: str):
    print(input.upper())


@cli.command()
def lower(input: str):
    print(input.lower())
