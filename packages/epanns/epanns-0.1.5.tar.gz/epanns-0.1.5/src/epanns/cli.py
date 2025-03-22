import typer

from .predict import run

app = typer.Typer()
app.command()(run)

if __name__ == "__main__":
    app()