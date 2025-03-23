import uvicorn
import click
import os
import sys
from pathlib import Path
from app.services.doc_generator import generate_documentation

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

@cli.command()
@click.option("--output", default="docs", help="Output directory for documentation.")
@click.option("--project-path", default=os.getcwd(), help="Path to the project to document.")
@click.option("--exclude", multiple=True, help="Directories to exclude from documentation.")
def generate(output, project_path, exclude):
    """Generate documentation for the project."""
    # Create output directory if it doesn't exist
    output_path = os.path.join(project_path, output)
    os.makedirs(output_path, exist_ok=True)
    
    click.echo(f"Generating documentation for project at {project_path}")
    click.echo(f"Documentation will be saved to {output_path}")
    
    try:
        generate_documentation(
            project_path=project_path, 
            output_dir=output_path,
            excluded_dirs=list(exclude)
        )
        click.echo("Documentation generated successfully!")
        click.echo(f"Run 'fastapi-autodoc runserver' to view the documentation")
    except Exception as e:
        click.echo(f"Error generating documentation: {str(e)}")
        click.echo("Creating a placeholder documentation page instead")
        with open(os.path.join(output_path, "index.html"), "w") as f:
            f.write(f"""<!DOCTYPE html>
                    
        <html>
        <head>
            <title>Project Documentation</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                h1 {{ color: #333; }}
                .error {{ color: #e74c3c; background: #fadbd8; padding: 10px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1>Documentation for {os.path.basename(project_path)}</h1>
            <p>An error occurred while generating documentation:</p>
            <div class="error">
                <pre>{str(e)}</pre>
            </div>
            <p>Please check your project structure and try again.</p>
        </body>
        </html>""")
    
    click.echo("Done!")

if __name__ == "__main__":
    cli()