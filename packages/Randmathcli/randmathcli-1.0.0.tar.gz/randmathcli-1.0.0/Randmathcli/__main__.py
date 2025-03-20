import click
import random

@click.command()
def cli():
    a = random.randint(1, 1000)
    b = random.randint(1, 1000)
    rand = random.randint(1, 4)
    click.echo("Randmathcli")
    click.echo("A Random Math Problem Generator") 
    click.echo("Copyright (c) 2025 by Mahdi Ruiz")
    click.echo("-----------------------------")
    if rand == 1:
     click.echo(f"{a} + {b} = {a + b}")
    if rand == 2:
     click.echo(f"{a} - {b} = {a - b}")
    if rand == 3:
     click.echo(f"{a} * {b} = {a * b}")
    if rand == 4:
     click.echo(f"{a} / {b} = {a / b}")

if __name__ == "__main__":
    cli()