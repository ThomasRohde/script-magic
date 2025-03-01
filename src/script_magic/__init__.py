import click

# Import command implementations
from script_magic.create import cli as create_command
from script_magic.run import cli as run_command
from script_magic.list import cli as list_command
from script_magic.delete import cli as delete_command

@click.group()
def sm():
    """Script Magic - A tool for creating and running Python scripts with GitHub Gists."""
    pass

# Register commands
sm.add_command(create_command, name='create')
sm.add_command(run_command, name='run')
sm.add_command(list_command, name='list')
sm.add_command(delete_command, name='delete')

if __name__ == '__main__':
    sm()
