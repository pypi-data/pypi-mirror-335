import typer

app = typer.Typer(add_completion=False)


@app.command()
def playwright(reverse: bool = typer.Option(False, "--reverse", "-r")):
    from ..playwright.route import RouteTool
    from ..playwright.codegen import CodeGen
    RouteTool.fix_package(reverse)
    CodeGen.fix_package(reverse)
