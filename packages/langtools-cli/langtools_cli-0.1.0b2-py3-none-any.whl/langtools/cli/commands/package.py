import os
import shutil
import subprocess
import typer
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from langtools.cli.console import console

app = typer.Typer(
    help="Package management commands",
    context_settings={"help_option_names": ["-h", "--help"]}
)

def pack_and_upload(file_path: str, package_version: str, feed_name: str):
    """Pack and upload a Python file to a feed.
    
    Args:
        file_path: Path to the Python file to pack
        package_version: Version for the package
        feed_name: Target feed URL for upload
    """
    # Ensure the file exists
    if not os.path.isfile(file_path):
        console.print(f"[red]Error: File '{file_path}' does not exist.[/red]")
        raise typer.Exit(code=1)

    # Create a temporary directory for the package
    package_name = os.path.splitext(os.path.basename(file_path))[0]
    temp_dir = f"{package_name}_package"
    os.makedirs(temp_dir, exist_ok=True)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Copy the Python file
        task = progress.add_task("Copying Python file...", total=None)
        shutil.copy(file_path, os.path.join(temp_dir, f"{package_name}.py"))
        progress.update(task, completed=True)

        # Create setup.py
        progress.add_task("Creating setup.py...", total=None)
        setup_content = f"""from setuptools import setup

setup(
    name='{package_name}',
    version='{package_version}',
    py_modules=['{package_name}'],
    install_requires=[],
)
"""
        with open(os.path.join(temp_dir, "setup.py"), "w") as setup_file:
            setup_file.write(setup_content)
        
        try:
            # Build the package
            task = progress.add_task("Building package...", total=None)
            subprocess.run(["python", "setup.py", "sdist"], cwd=temp_dir, check=True, capture_output=True)
            progress.update(task, completed=True)

            # Upload the package
            dist_dir = os.path.join(temp_dir, "dist")
            package_files = os.listdir(dist_dir)
            if package_files:
                package_file = package_files[0]
                console.print(Panel(f"Package '[green]{package_file}[/green]' created successfully"))
                
                task = progress.add_task("Uploading package...", total=None)
                subprocess.run(["twine", "upload", "--repository-url", feed_name, "dist/*"], 
                             cwd=temp_dir, check=True, capture_output=True)
                progress.update(task, completed=True)
                
                console.print(Panel(f"[green]Successfully[/green] uploaded package '[blue]{package_name}[/blue].[blue]{package_version}[/blue]' to feed [yellow]{feed_name}[/yellow]"))
            else:
                console.print("[red]Error: No package files found.[/red]")
                raise typer.Exit(code=1)
        finally:
            # Clean up
            task = progress.add_task("Cleaning up...", total=None)
            shutil.rmtree(temp_dir)
            progress.update(task, completed=True)

@app.command("upload")
def upload(
    file: str = typer.Option(None, "-f", "--file", help="the python file to pack"),
    version: str = typer.Option(None, "-v", "--version", help="the python package version"),
    feed: str = typer.Option(None, "--feed", help="the feed name to upload the package to")
):
    """Pack a Python file and upload it to a feed."""
    pack_and_upload(file, version, feed)