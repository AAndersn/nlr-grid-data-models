import typer
from gdm.cli.reducer import reduce

app = typer.Typer()
app.command()(reduce)
