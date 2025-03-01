"""
Script Magic CLI - Main entry point for the script-magic application.
"""
import os
import sys
import click

# Import command implementations
from commands.create import cli as create_command
from commands.run import cli as run_command

@click.group()
def sm():
    """Script Magic - A tool for creating and running Python scripts with GitHub Gists."""
    pass

# Register commands
sm.add_command(create_command, name='create')
sm.add_command(run_command, name='run')

if __name__ == '__main__':
    sm()
