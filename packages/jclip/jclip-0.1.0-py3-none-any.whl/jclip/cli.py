import typer

from .copier import JClip

app = typer.Typer()
app.command()(JClip)

if __name__ == "__main__":
    app()