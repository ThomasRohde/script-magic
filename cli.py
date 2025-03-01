import click

@click.group()
def sm():
    """Script Magic - A tool for creating and running Python scripts with GitHub Gists."""
    pass

@sm.command()
@click.argument('script_name')
@click.argument('prompt')
@click.option('--preview', '-p', is_flag=True, help='Preview the script before creating it')
def create(script_name, prompt, preview):
    """Create a new Python script from a prompt and store it in a GitHub Gist."""
    # This will be replaced with actual implementation from commands/create.py
    click.echo(f"Creating script '{script_name}' with prompt: {prompt}")
    if preview:
        click.echo("Preview mode enabled")

@sm.command()
@click.argument('script_name')
@click.argument('params', nargs=-1)
def run(script_name, params):
    """Run a Python script stored in a GitHub Gist."""
    # This will be replaced with actual implementation from commands/run.py
    click.echo(f"Running script '{script_name}'")
    if params:
        click.echo(f"With parameters: {params}")

if __name__ == '__main__':
    sm()
