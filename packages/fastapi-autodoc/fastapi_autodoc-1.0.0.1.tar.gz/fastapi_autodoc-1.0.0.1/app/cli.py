import uvicorn
import click
from app.main import create_app

@click.group()
def cli():
    """CLI for FastAPI AutoDoc."""
    pass

@cli.command()
@click.option("--host", default="127.0.0.1", help="Host to run the server on.")
@click.option("--port", default=8000, help="Port to run the server on.")
@click.option("--reload", is_flag=True, help="Enable auto-reload.")
def runserver(host, port, reload):
    """Run the FastAPI server."""
    uvicorn.run("app.main:app", host=host, port=port, reload=reload)

if __name__ == "__main__":
    cli()