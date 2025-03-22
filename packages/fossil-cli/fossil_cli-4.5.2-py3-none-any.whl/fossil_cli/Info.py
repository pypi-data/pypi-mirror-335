from click import command

from .utils import fossil, shell


@command()
def info():
    "Aporta informacion acerca del arbol actual"
    shell(f"{fossil} info")
