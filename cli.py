"""
Script Magic CLI - Main entry point for the script-magic application.
"""
import os
import sys
import click

# Import command implementations
from commands.create import cli as create_command

@click.group()
def sm():
    """Script Magic - A tool for creating and running Python scripts with GitHub Gists."""
    pass

# Register the create command
sm.add_command(create_command, name='create')

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
