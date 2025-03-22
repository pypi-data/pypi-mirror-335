from click import command

from .utils import confirm, echo, error, fossil, prompt, run, run_pre_pos, select
from .Version import get_version


def help_branch():
    """
    Un texto de ayuda sobre las diferentes ramas y su uso
    """
    echo("Ayuda sobre las diferentes ramas y su uso")
    echo(
        "trunk: Rama madre de 'develop' y 'hotfix', es la principal y no se debe guardar cambios directamente en ella"
    )
    echo(
        "  hotfix: Rama que se usa para corregir bug, se cierra contra 'trunk' al finalizar el arreglo"
    )
    echo(
        "  develop: Rama madre de 'feature' y 'release', es la que cordina el desarrollo y lo mantiene escalonado y no debe guardar cambios directamente en ella"
    )
    echo(
        "    feature: Rama para agregar nuevas caracteristicas, se cierra contra 'develop', y 'trunk' si fuera nesesario, al finalizarla"
    )
    echo(
        "    release: Rama para preparar un lanzamiento, se cierra contra 'develop' y 'trunk' al finalizarla"
    )


@command()
def branch():
    """
    Manipula los ramas convenientemente
    """

    current_branch = run(f"{fossil} branch current")
    version = get_version(current_branch)

    echo(f"Rama actual     {current_branch}")
    echo(f"Version actual  {version}")

    if run(f"{fossil} changes"):
        error("Existen cambios realice un commit primero")

    run_pre_pos("pre_branch", **locals())

    if current_branch == "trunk":
        if not confirm(
            "En esta rama solo se pueden adicionar ramas 'hotfix', estas seguro de continuar?"
        ):
            help_branch()
            return

        version = version.next_version("prerelease", "rev")
        br_name = "hotfix-" + prompt("Escriba nombre de la rama")

        if confirm(f"Estas seguro de crear la rama {br_name}?"):
            run_pre_pos("pre_branch_trunk", **locals())

            run(f"{fossil} branch new {br_name} {current_branch}")
            run(f"{fossil} tag add v{str(version)} {br_name}")
            run(f"{fossil} update {br_name}")

            run_pre_pos("pos_branch_trunk", **locals())

    elif current_branch == "develop":
        if not confirm(
            "En esta rama solo se pueden adicionar ramas 'feature' y 'release', estas seguro de continuar?"
        ):
            help_branch()
            return

        branchs = [
            "feature: Una rama para agregar una caracteristica",
            "release: Una rama para arregrar el codigo antes de publicarlo",
        ]

        branch = select("Selecciona el tipo de rama a crear", choices=branchs)

        if branch.startswith("feature"):
            br_name = "feature-" + prompt("Escriba nombre de la rama")
            version = version.next_version("minor").next_version("prerelease", "dev")
        else:
            br_name = f"release-{str(version)}"
            version = version.next_version("prerelease")

        if confirm(f"Estas seguro de crear la rama {br_name}?"):
            run_pre_pos("pre_branch_develop", **locals())

            run(f"{fossil} branch new {br_name} {current_branch}")
            run(f"{fossil} tag add v{str(version)} {br_name}")
            run(f"{fossil} update {br_name}")

            run_pre_pos("pos_branch_develop", **locals())

    elif current_branch.startswith("feature"):
        version = version.finalize_version()
        if confirm(f"Estas seguro de unificar la rama {current_branch} en develop?"):
            run_pre_pos("pre_branch_feature", **locals())

            run(f"{fossil} update develop")
            run(f"{fossil} merge --integrate {current_branch}")
            run(
                f'{fossil} commit -m "Unificando la rama {current_branch}" --no-warnings'
            )
            run(f"{fossil} tag add v{str(version)} develop")

            if confirm("Deseas unificar la rama develop en trunk?"):
                run(f"{fossil} update trunk")
                run(f"{fossil} merge develop")
                run(f'{fossil} commit -m "Unificando la rama develop" --no-warnings')
                run(f"{fossil} tag add v{str(version)} trunk")

                if confirm("Deseas regresar a la rama develop?"):
                    run(f"{fossil} update develop")

            run_pre_pos("pos_branch_feature", **locals())

    elif current_branch.startswith("release"):
        version = version.finalize_version()
        if confirm(f"Estas seguro de cerrar la version {version}?"):
            run_pre_pos("pre_branch_release", **locals())

            run(f"{fossil} update develop")
            run(f"{fossil} merge --integrate {current_branch}")
            run(
                f'{fossil} commit -m "Unificando la rama {current_branch}" --no-warnings'
            )
            run(f"{fossil} tag add v{str(version)} develop")

            run(f"{fossil} update trunk")
            run(f"{fossil} merge develop")
            run(f'{fossil} commit -m "Unificando la rama develop" --no-warnings')
            run(f"{fossil} tag add v{str(version)} trunk")

            if confirm("Deseas regresar a la rama develop?"):
                run(f"{fossil} update develop")

            run_pre_pos("pos_branch_release", **locals())

    elif current_branch.startswith("hotfix"):
        version = version.finalize_version()

        if confirm(f"Estas seguro de unificar la rama {current_branch} en trunk?"):
            run_pre_pos("pre_branch_hotfix", **locals())
            if confirm(f"Deseas unificar la rama {current_branch} en develop?"):
                run(f"{fossil} update develop")
                run(f"{fossil} merge {current_branch}")
                run(
                    f'{fossil} commit -m "Unificando la rama {current_branch}" --no-warnings'
                )
                run(f"{fossil} tag add v{str(version)} develop")

            run(f"{fossil} update trunk")
            run(f"{fossil} merge --integrate {current_branch}")
            run(
                f'{fossil} commit -m "Unificando la rama {current_branch}" --no-warnings'
            )
            run(f"{fossil} tag add v{str(version)} trunk")

            run_pre_pos("pos_branch_hotfix", **locals())

    run_pre_pos("pos_branch", **locals())
