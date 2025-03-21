import typer
from .modules.map import genomeMap
# from .modules.isoform import isoform
# from .modules.detectMod import detectMod
# from .modules.isoformAS import isoformAS
# from .modules.nascentRNA import nascentRNA

app = typer.Typer(add_completion=False)

@app.callback()
def callback():
    """
    nanoISO is a toolkit for analyzing and processing nanopore cDNA data.
    """

app.command(name="map")(genomeMap)
# app.command(name="isoform")(isoform)
# app.command(name="isoformAS")(isoformAS)
# app.command(name="detectMod")(detectMod)
# app.command(name="nascentRNA")(nascentRNA)


if __name__ == "__main__":
    app()