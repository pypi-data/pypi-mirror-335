import typer

app = typer.Typer(add_completion=False)


@app.command()
def clean(path):
    from ..git import git_clean_dir
    git_clean_dir(path)


@app.command()
def fetch_min(url, tag, path):
    from ..git import git_fetch_min
    git_fetch_min(url, tag, path)
