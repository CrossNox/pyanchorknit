from pathlib import Path

import typer

from pyanchorknit.weaving import weaving

app = typer.Typer()


@app.command()
def main(
    img: Path = typer.Argument(..., help="Path to input image"),
    img_out: Path = typer.Option("./weaved.png", help="Path to output image"),
    traces_out: Path = typer.Option(
        "./traces.json", help="Path to output json of traces"
    ),
    n_edges: int = typer.Option(512, help="Number of points around the edge"),
    intensity_threshold: float = typer.Option(
        0.1,
        min=0,
        max=1,
        help="Min intensity threshold respect to the max intensity threshold to process",
    ),
    maxlines: int = typer.Option(2000, help="Max number of traces"),
    n_jobs: int = typer.Option(8, help="Max number of jobs to use"),
):
    """Make weaving image."""
    weaving(
        img,
        img_out=img_out,
        traces_out=traces_out,
        n_edges=n_edges,
        maxlines=maxlines,
        n_jobs=n_jobs,
        intensity_threshold=intensity_threshold,
    )
