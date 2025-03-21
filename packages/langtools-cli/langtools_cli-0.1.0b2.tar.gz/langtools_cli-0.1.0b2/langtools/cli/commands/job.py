from typing import Optional, Set
import typer
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from langtools.cli import authentication  # from core package
from langtools.cli.console import console
from ray.job_submission import JobSubmissionClient

job = typer.Typer(
    help="Job management commands",
    context_settings={"help_option_names": ["-h", "--help"]}
)

# Valid parameters for Ray's JobSubmissionClient.submit_job
VALID_SUBMIT_PARAMS: Set[str] = {
    "entrypoint", "job_id", "runtime_env", "metadata", "submission_id",
    "entrypoint_num_cpus", "entrypoint_num_gpus", "entrypoint_memory",
    "entrypoint_resources"
}

# Valid parameters for runtime_env configuration
VALID_RUNTIME_ENV_PARAMS: Set[str] = {
    "working_dir", "py_modules", "py_executable", "excludes",
    "pip", "uv", "conda", "env_vars", "nsight", "image_uri", "config"
}


def submit_package(file_name: str, ray_cluster: str, requirements: Optional[str] = None,
                   feed: Optional[str] = None, num_cpus: int = 1, app_type: str = 'job',
                   target_host: str = 'ray', ray_args: Optional[list] = None, dry_run: bool = False):
    """Submit a package to a cluster.
    
    Args:
        file_name: Path to the Python file to submit
        ray_cluster: URL of the Ray cluster
        requirements: Optional path to requirements.txt
        feed: Optional feed URL for dependencies
        num_cpus: Number of CPUs to allocate
        app_type: Type of job ('job' by default)
        target_host: Target platform for submission ('ray' by default)
    """
    if target_host != 'ray':
        raise ValueError("Currently only 'ray' platform is supported for deployment")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(f"Preparing job submission for {target_host} platform...", total=None)
        headers = authentication.update_header_with_authentication(ray_cluster)
        access_token, _ = authentication.acquire_obo_tokens()
        runtime_env = {
            "working_dir": "./",
            "env_vars": {"OBO_USER_ASSERTION": access_token} if access_token else {}
        }
        
        if requirements:
            progress.update(task, description="Configuring requirements...")
            runtime_env["pip"] = {"packages": requirements}
            if not feed:
                feed = "msasg.pkgs.visualstudio.com/WebXT/_packaging/Repo/pypi/simple/"
            if feed.startswith("http://") or feed.startswith("https://"):
                feed = feed.split("://", 1)[1]
            runtime_env["pip"]["index_url"] = f"https://ServerlessPlatform:{{token}}@{feed}"

        progress.update(task, description=f"Submitting to {target_host} cluster as {app_type}...")
        # Build submit arguments
        submit_kwargs = {
            "entrypoint": f"python {file_name}",
            "runtime_env": runtime_env,
            "entrypoint_num_cpus": num_cpus
        }

        # Process Ray-specific arguments
        if ray_args:
            i = 0
            while i < len(ray_args):
                arg = ray_args[i]
                if arg.startswith("--"):
                    key = arg[2:].replace("-", "_")  # Convert --arg-name to arg_name
                    
                    # Check if next argument exists and is a value (not another option)
                    if i + 1 < len(ray_args) and not ray_args[i + 1].startswith("--"):
                        value = ray_args[i + 1]
                        
                        # Warn about unknown parameters
                        if key not in VALID_SUBMIT_PARAMS and key not in VALID_RUNTIME_ENV_PARAMS:
                            console.print(f"[yellow]Warning:[/yellow] Unknown parameter '{key}'")
                        
                        # Handle runtime_env fields - all params are passed through but warn if unknown
                        if key not in VALID_SUBMIT_PARAMS:  # If not a submit param, treat as runtime_env
                            runtime_env = submit_kwargs.get("runtime_env", {})
                            try:
                                # Try parsing as JSON for complex values
                                import json
                                runtime_env[key] = json.loads(value)
                            except json.JSONDecodeError as e:
                                # For simple string values
                                runtime_env[key] = value
                            submit_kwargs["runtime_env"] = runtime_env
                        
                        # Handle direct submit_job parameters
                        elif key in ["entrypoint_memory", "entrypoint_num_gpus"]:
                            try:
                                submit_kwargs[key] = float(value)
                            except ValueError:
                                console.print(f"[red]Error:[/red] {key} must be a number")
                                return
                        
                        # Handle dictionary parameters
                        elif key in ["entrypoint_resources", "metadata"]:
                            try:
                                import json
                                submit_kwargs[key] = json.loads(value)
                            except json.JSONDecodeError:
                                console.print(f"[red]Error:[/red] {key} must be valid JSON")
                                return
                        
                        # Handle string parameters
                        elif key in ["job_id", "submission_id"]:
                            submit_kwargs[key] = value
                        
                        i += 2
                    else:
                        # Flag without value
                        if key not in VALID_SUBMIT_PARAMS and key not in VALID_RUNTIME_ENV_PARAMS:
                            console.print(f"[yellow]Warning:[/yellow] Unknown parameter '{key}'")
                        submit_kwargs[key] = True
                        i += 1
                else:
                    i += 1

            # Merge runtime_env with existing settings
            if "runtime_env" in submit_kwargs:
                # Update runtime_env but preserve OBO_USER_ASSERTION in env_vars
                user_env_vars = submit_kwargs["runtime_env"].get("env_vars", {})
                if "env_vars" in runtime_env:
                    user_env_vars = {**user_env_vars, **{"OBO_USER_ASSERTION": runtime_env["env_vars"]["OBO_USER_ASSERTION"]}} if "OBO_USER_ASSERTION" in runtime_env["env_vars"] else user_env_vars
                submit_kwargs["runtime_env"].update(runtime_env)
                submit_kwargs["runtime_env"]["env_vars"] = user_env_vars
                submit_kwargs["runtime_env"] = runtime_env

        if dry_run:
            # Organize parameters by type for clear display
            console.print(submit_kwargs)
        else:
            # Actually submit the job
            client = JobSubmissionClient(address=ray_cluster, headers=headers)
            job_id = client.submit_job(**submit_kwargs)
            progress.update(task, completed=True)
            
            console.print(Panel(
                f"[green]Successfully[/green] submitted {app_type} '[blue]{file_name}[/blue]' to {target_host} cluster\n" +
                f"[yellow]Cluster:[/yellow] {ray_cluster}\n" +
                f"[yellow]Job ID:[/yellow] {job_id}"
            ))

def print_help():
    """Print formatted help message using Rich"""
    from rich import box
    from rich.text import Text
    from rich.table import Table

    # Create main table for layout
    layout = Table(box=box.ROUNDED, show_header=False, padding=(0,1))
    layout.add_column("content", no_wrap=False)

    # Title and description
    layout.add_row(Text("Submit a job package to a specified platform.", style="bold cyan"))
    layout.add_row(Text("After -- you can pass Ray options that will be forwarded to the cluster.\n", style="yellow"))

    # Submit Parameters
    params_table = Table(show_header=False, box=None, padding=(0,2))
    params_table.add_column("param", style="green")
    params_table.add_column("desc")
    params_table.add_row(Text("Submit Job Parameters:", style="bold"))
    params_table.add_row("--job-id TEXT", "Specific job ID")
    params_table.add_row("--submission-id TEXT", "Submission ID")
    params_table.add_row("--entrypoint-memory N", "Memory in MB")
    params_table.add_row("--entrypoint-num-gpus N", "Number of GPUs")
    params_table.add_row("--metadata JSON", "Additional metadata as JSON")
    params_table.add_row("--runtime-env JSON", "runtime environment parameters as JSON")
    layout.add_row(params_table)

    # Runtime Environment
    runtime_table = Table(show_header=False, box=None, padding=(0,2))
    runtime_table.add_column("param", style="green")
    runtime_table.add_column("desc")
    runtime_table.add_row(Text("\nRuntime Environment Parameters:", style="bold"))
    
    # Working Directory
    runtime_table.add_row(Text("Working Directory:", style="bold yellow"))
    runtime_table.add_row("--working-dir PATH", "Local dir, zip, or URI\n  Example: \"./project\" or \"s3://bucket/project.zip\"")
    
    # Python Settings
    runtime_table.add_row(Text("Python Settings:", style="bold yellow"))
    runtime_table.add_row("--py-modules LIST", "Module paths or URIs\n  Example: Use quotes: --py-modules '[\"./module\", \"s3://bucket/lib.whl\"]'")
    runtime_table.add_row("--py-executable CMD", "Custom Python command\n  Example: \"python -m debugpy\"")
    runtime_table.add_row("--excludes LIST", "Exclude patterns\n  Example: '[\"*.pyc\", \"temp/\"]'")
    
    # Package Management
    runtime_table.add_row(Text("\nPackage Management:", style="bold yellow"))
    runtime_table.add_row("--pip JSON|PATH", "Install pip packages:\n  - JSON list: '[\"tensorflow\", \"pytorch\"]'\n  - Path: \"./requirements.txt\"\n  - Config: '{\"packages\":[\"tensorflow\"]}'")
    runtime_table.add_row("--conda JSON|PATH", "Conda environment:\n  - JSON: '{\"dependencies\":[\"pytorch\"]}'\n  - Path: \"./environment.yml\"\n  - Name: \"existing_env\"")
    
    # Environment
    runtime_table.add_row(Text("\nEnvironment:", style="bold yellow"))
    runtime_table.add_row("--env-vars JSON", "Set environment variables\n  Example: '{\"CUDA_VISIBLE\": \"0,1\"}'")
    runtime_table.add_row("--image-uri TEXT", "Docker image for worker\n  Example: \"anyscale/ray:2.31.0\"")
    layout.add_row(runtime_table)

    # Examples
    examples = Table(show_header=False, box=None, padding=(0,2))
    examples.add_column("example", style="green")
    examples.add_row(Text("\nQuick Examples:", style="bold"))
    examples.add_row("# Basic job")
    examples.add_row("langtools job submit -f app.py -c URL -- --working-dir ./app")
    examples.add_row("\n# With GPU and env vars")
    examples.add_row("langtools job submit -f app.py -c URL -- \\")
    examples.add_row("    --entrypoint-num-gpus 1 \\")
    examples.add_row("    --env-vars '{\"CUDA_VISIBLE\":\"0\"}'")
    layout.add_row(examples)

    # Notes
    notes = Table(show_header=False, box=None, padding=(0,2))
    notes.add_column("note")
    notes.add_row(Text("\nNotes:", style="bold"))
    notes.add_row("- All options after -- go to Ray")
    notes.add_row("- Unknown options show warning but pass through")
    notes.add_row("- Quote JSON values: --env-vars '{\"KEY\":\"VALUE\"}'")
    layout.add_row(notes)

    console.print(layout)

def show_help(value: bool, ctx: typer.Context):
    """Show both default help and detailed help"""
    if value:  # Only show help when the flag is True
        # Get the default help
        default_help = ctx.get_help()
        console.print(default_help)
        console.print("\n=== Detailed Help ===\n")
        print_help()
        raise typer.Exit()
    return value  # Return the flag value for normal processing

@job.command(context_settings={
    "allow_extra_args": True,
    "ignore_unknown_options": True
})
def submit(
    ctx: typer.Context,
    help: bool = typer.Option(False, "-h", "--help", callback=show_help, is_eager=True, help="Show help message and detailed options"),
    file: str = typer.Option(None, "-f", "--file", help="the python file to submit to cluster"),
    cluster: str = typer.Option(None, "-c", "--cluster", help="the cluster url where the job will be submitted"),
    requirements: Optional[str] = typer.Option(None, "-r", "--requirements", help="path to the requirements.txt file for additional dependencies"),
    feed: Optional[str] = typer.Option(None, "--feed", help="feed url for additional dependencies"),
    num_cpus: int = typer.Option(1, "--num-cpus", help="number of cpus to allocate for the entrypoint"),
    type: str = typer.Option("job", "--type", "-t", help="type of job to submit (NOTE: currently only supports 'job' type)"),
    target_host: str = typer.Option("ray", "--target-host", help="target platform for submission (NOTE: currently only supports 'ray' platform)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be submitted without actually submitting the job"),
):
    """Submit a job package to a specified platform.
    Use --help to see detailed parameter information."""
    ray_args = ctx.args if ctx.args else None
    submit_package(file, cluster, requirements, feed, num_cpus, type, target_host, ray_args, dry_run)