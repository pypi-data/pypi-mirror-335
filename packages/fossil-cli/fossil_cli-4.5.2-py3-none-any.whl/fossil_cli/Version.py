from click import command
from semver import VersionInfo

from .utils import echo, fossil, run


@command()
def version():
    "Muestra la version del repositorio"
    current_branch = run(f"{fossil} branch current")
    echo(str(get_version(current_branch)) + ", branch: " + current_branch)


def get_version(check_in):
    tags = run(f"{fossil} tag list {check_in}").splitlines()

    for tag in tags:
        if VersionInfo.is_valid(tag[1:]):  # Se le quita el "v"
            return VersionInfo.parse(tag[1:])
