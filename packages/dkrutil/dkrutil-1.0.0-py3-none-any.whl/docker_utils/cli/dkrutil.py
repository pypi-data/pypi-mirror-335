import rich_click as click

from docker_utils.cli.containers import ps
from docker_utils.cli.images import images
from docker_utils.cli.volumes import volumes


@click.group()
def dkrutil():
    pass


dkrutil.add_command(volumes)
dkrutil.add_command(images)
dkrutil.add_command(ps)

if __name__ == "__main__":
    dkrutil()
