import typer
from langtools.cli.commands import job

app = typer.Typer(
    help="LangTools CLI for package management and job submission",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]}
)

# Add command groups
# app.add_typer(package.app, name="package")
app.add_typer(job.job, name="job")

def main():
    """Entry point for the CLI application."""
    app()

if __name__ == "__main__":
    main()