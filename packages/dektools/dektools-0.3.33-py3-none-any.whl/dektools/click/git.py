import typer
from typing_extensions import Annotated

app = typer.Typer(add_completion=False)


@app.command()
def clean(path):
    from ..git import git_clean_dir
    git_clean_dir(path)


@app.command()
def fetch_min(url, tag, path):
    from ..git import git_fetch_min
    git_fetch_min(url, tag, path)


@app.command()
def remove_tag(tag, path: Annotated[str, typer.Argument()] = ""):
    from ..git import git_remove_tag
    git_remove_tag(tag, path)
