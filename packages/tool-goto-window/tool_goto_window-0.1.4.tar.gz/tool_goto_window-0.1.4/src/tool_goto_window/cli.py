import typer
from tool_goto_window.main import switch_to_window, show, init

app = typer.Typer()

# Default command for switching windows
app.command(name="switch")(switch_to_window)

# Add recent windows command
app.command(name="recent")(show)
app.command(name="init")(init)

# Make switch_to_window the default when no command is specified
@app.callback(invoke_without_command=True)
def callback(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        typer.run(switch_to_window)

if __name__ == "__main__":
    app()