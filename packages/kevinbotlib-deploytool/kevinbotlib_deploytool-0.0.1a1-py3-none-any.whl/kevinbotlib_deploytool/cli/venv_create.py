from contextlib import contextmanager
from pathlib import Path

import click
import paramiko
from rich.console import Console
from rich.panel import Panel

from kevinbotlib_deploytool import deployfile
from kevinbotlib_deploytool.sshkeys import SSHKeyManager

console = Console()


def check_py_location(ssh: paramiko.SSHClient, python_location: str):
    _, _, stderr = ssh.exec_command(f"{python_location} --version")
    error = stderr.read().decode().strip()
    if error:
        console.print(f"[red]Error location remote Python executable: {error}[/red]")
        raise click.Abort
    console.print(f"[green]✔ Remote Python executable is valid: {python_location}[/green]")
    return error


def check_venv(ssh: paramiko.SSHClient, python_location: str):
    _, stdout, stderr = ssh.exec_command(f"{python_location} -m venv --help")
    output = stdout.read().decode().strip()
    error = stderr.read().decode().strip()
    if error:
        console.print(f"[red]Error checking venv module: {error}[/red]")
        raise click.Abort
    console.print("[bold green]✔ Venv module is available in remote Python installation[/bold green]")
    return output


def run_py_test(spinner, ssh):
    spinner.status = "Running test command"
    _, stdout, stderr = ssh.exec_command("python -c 'print(\"Hello world!\")'")
    output = stdout.read().decode().strip()
    error = stderr.read().decode().strip()
    if error:
        console.print(f"[red]Error running test command: {error}[/red]")
        raise click.Abort
    console.print(f"[green]Test command output: {output}[/green]")
    if output != "Hello world!":
        console.print(f"[red]Test command output does not match expected value: {output}[/red]")
        raise click.Abort

    console.print("[bold green]✔ Test command ran successfully[/bold green]")


def check_venv_exists(ssh):
    _, stdout, stderr = ssh.exec_command("ls $HOME/robotenv")
    output = stdout.read().decode().strip()
    error = stderr.read().decode().strip()
    if output:
        console.print("[red]Virtual environment already exists at $HOME/robotenv[/red]")
        raise click.Abort
    console.print("Virtual environment does not exist at $HOME/robotenv, creating it...")
    return error


def compare_py_version_df(df, output):
    if df.python_version:
        # We only need to get the major and minor version
        remote_version = output.split()[1].split(".")[:2]
        remote_version = ".".join(remote_version)
        if remote_version == df.python_version:
            console.print(
                f"[bold green]✔ Remote Python version matches Deployfile:[/bold green] {remote_version}=={df.python_version}"
            )
        else:
            console.print(
                f"[bold yellow]WARN: Remote Python version does not match Deployfile:[/bold yellow] {remote_version}!={df.python_version}"
            )


def check_py_version(python_location, ssh):
    _, stdout, stderr = ssh.exec_command(f"{python_location} --version")
    output = stdout.read().decode().strip()
    error = stderr.read().decode().strip()
    if error:
        console.print(f"[red]Error getting remote Python version: {error}[/red]")
        raise click.Abort
    console.print(f"[green]Remote Python version: {output}[/green]")
    return output


@contextmanager
def rich_spinner(message: str, success_message: str | None = None):
    with console.status(f"[bold green]{message}...", spinner="dots") as spinner:
        try:
            yield spinner
        finally:
            if success_message:
                console.print(f"[bold green]\u2714 {success_message}")


@click.command("create")
@click.option(
    "-d",
    "--df-directory",
    default=".",
    help="Directory of the Deployfile",
    type=click.Path(file_okay=False, dir_okay=True, writable=True),
)
@click.option(
    "-p",
    "--python-location",
    default="/usr/bin/python3",
    help="Location of the Python executable",
    prompt=True,
    type=click.Path(exists=False, dir_okay=False, file_okay=True),
)
def create_venv_command(df_directory: str, python_location):
    """Create a virtual environment."""
    df = deployfile.read_deployfile(Path(df_directory) / "Deployfile.toml")

    # Connect over SSH
    key_manager = SSHKeyManager("KevinbotLibDeployTool")
    key_info = key_manager.list_keys()
    if df.name not in key_info:
        console.print(
            f"[red]Key '{df.name}' not found in key manager. Use `kevinbotlib ssh init` to create a new key`[/red]"
        )
        raise click.Abort

    private_key_path, _ = key_info[df.name]

    # Load the private key
    try:
        pkey = paramiko.RSAKey.from_private_key_file(private_key_path)
    except Exception as e:
        console.print(f"[red]Failed to load private key: {e}[/red]")
        raise click.Abort from e

    with rich_spinner("Beginning transport session"):
        try:
            sock = paramiko.Transport((df.host, df.port))
            sock.connect(username=df.user, pkey=pkey)
            host_key = sock.get_remote_server_key()
            sock.close()
        except Exception as e:
            console.print(Panel(f"[red]Failed to get host key: {e}", title="Host Key Error"))
            raise click.Abort from e

    console.print(Panel(f"[yellow]Host key for {df.host}:\n{host_key.get_base64()}", title="Host Key Confirmation"))
    if not click.confirm("Do you want to continue connecting?"):
        raise click.Abort

    with rich_spinner("Running commands via SSH") as spinner:
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # noqa: S507 # * this is ok, because the user is asked beforehand
            ssh.connect(hostname=df.host, port=df.port, username=df.user, pkey=pkey, timeout=10)

            # Check if the Python location is valid
            check_py_location(ssh, python_location)

            # Check version
            output = check_py_version(python_location, ssh)

            # Compare it with Deployfile
            compare_py_version_df(df, output)

            # Check if the virtual environment already exists
            check_venv_exists(ssh)

            # Check if the Python installation contains venv
            output = check_venv(ssh, python_location)

            # Create the virtual environment
            spinner.status = "Creating virtual environment"
            ssh.exec_command(f"{python_location} -m venv $HOME/robotenv")
            spinner.status = "Virtual environment created"
            console.print("[bold green]✔ Virtual environment created successfully[/bold green]")

            # Activate the virtual environment
            spinner.status = "Activating virtual environment"
            ssh.exec_command("source $HOME/robotenv/bin/activate")
            spinner.status = "Virtual environment activated"
            console.print("[bold green]✔ Virtual environment activated successfully[/bold green]")

            # Run a test
            run_py_test(spinner, ssh)

            ssh.close()
        except Exception as e:
            if not isinstance(e, click.Abort):
                console.print(f"[red]SSH connection failed: {e!r}[/red]")
            raise
