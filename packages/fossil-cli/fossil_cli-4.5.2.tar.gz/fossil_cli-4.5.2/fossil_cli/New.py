from pathlib import Path

from click import command, option

from .utils import checkbox, error, fossil, prompt, run, run_pre_pos


@command()
@option("-f", "--filename", type=Path, help="Archivo del repositorio")
@option("-v", "--version", type=Path, help="Version Inicial", default="0.0.0")
def new(filename, version):
    """
    Crea un nuevo repositorio.
    """

    repo = filename or Path(prompt("Archivo del repositorio", default=".fossil"))
    if repo.is_absolute():
        error(f"{repo} no es relativo")
    if repo.exists():
        error(f"Ya existe el repositorio {repo}")

    run_pre_pos("pre_new", **locals())

    # Create the repo
    run(f"{fossil} init {repo}")

    # Opening the repo
    run(f"{fossil} open --force {repo}")

    # Append initial files
    choices = run(f"{fossil} extras --ignore *.pyc").splitlines()
    files = checkbox("Escoja los archivos iniciales", choices=choices)
    run(f"{fossil} add {' '.join(files)}")
    run(f'{fossil} commit -m "Initial Commit" --no-warnings')
    run(f"{fossil} tag add v{version} trunk")

    # Create developer branch
    run(f"{fossil} branch new develop trunk")
    run(f"{fossil} tag add v{version} develop")
    run(f"{fossil} update develop")

    run_pre_pos("pos_new", **locals())
