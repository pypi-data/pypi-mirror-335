from click import command, option

from .utils import confirm, echo, error, fossil, prompt, run, run_pre_pos, select
from .Version import get_version


@command()
@option("-ct", "--change-type", help="Tipo de cambio del commit")
@option("-cc", "--change-concept", help="Concepto de cambio del commit")
@option("-cb", "--change-body", help="Cuerpo del commit")
def commit(change_type, change_concept, change_body):
    """
    Corre un commit al repositorio.
    """
    current_branch = run(f"{fossil} branch current")

    if current_branch in ("trunk", "develop"):
        error("Los cambios se deben realizar en una rama dedicada")

    if not run(f"{fossil} changes"):
        error("No existen cambios")

    version = get_version(current_branch)

    echo(f"Rama actual     {current_branch}")
    echo(f"Version actual  {version}")

    version = version.next_version("prerelease")

    changes = {
        "new: Una nueva caracteristica": [
            "feat: Adicionando una caracteristica",
            "docs: Adicionando la documentacion",
            "test: Adicionando pruebas",
            "cancelar: Cancelando la operacion",
        ],
        "changes: Cambio que mejora el codigo en general": [
            "docs: Cambio solo en la documentacion",
            "style: Cambio que afectan el estilo del codigo",
            "refactor: El codigo cambia pero no corrige un bug o es una nueva caracteristica",
            "perf: Cambio que mejora el codigo en general",
            "build: Cambios que afecta el sistema de build o las librerias externas",
            "ci: Cambios sobre los script CI o sobre el sistema",
            "cancelar: Cancelando la operacion",
        ],
        "fixes: Arreglo de bugs": [
            "fix: Arreglo de bugs",
            "build: Arreglo de bugs que afecta el sistema de build o las librerias externas",
            "ci: Arreglo de bugs sobre los script CI o sobre el sistema",
            "cancelar: Cancelando la operacion",
        ],
        "breaks: Eliminando codigo no usado": [
            "feat: Eliminando una caracteristica",
            "docs: Eliminando la documentacion",
            "test: Eliminando pruebas",
            "cancelar: Cancelando la operacion",
        ],
        "cancelar: Cancelando la operacion": [],
    }

    if not change_type:
        change_type = select(
            "Selecciona el tipo de cambio del commit", choices=changes.keys()
        )

    if change_type.startswith("cancelar"):
        error("Cancelando")

    if not change_concept:
        change_concept = select(
            "Selecciona el concepto de cambio del commit",
            choices=changes[change_type],
        ).split(":")[0]

    if change_concept.startswith("cancelar"):
        error("Cancelando")

    change_type = change_type.split(":")[0]

    if not change_body:
        change_body = prompt("Escriba el cuerpo del commit (c para cancelar)")

    if change_body in (
        "c",
        "cancelar",
        "cancel",
        "q",
        "quitar",
        "quit",
        "e",
        "exit",
        "s",
        "salir",
    ):
        error("Cancelando")

    commit = f"{change_type}({change_concept}): {change_body}"

    echo(f"commit: {commit}")
    if confirm("Estas seguro de aplicar el commit?"):
        run_pre_pos("pre_commit", **locals())

        run(f'{fossil} commit -m "{commit}" --no-warnings')
        run(f"{fossil} tag add v{str(version)} {current_branch}")

        run_pre_pos("pos_commit", **locals())
