import sys
import typer

app = typer.Typer(add_completion=False)


@app.command(name='port')
def port_(port, host='localhost'):
    from ..net import is_port_in_use
    if is_port_in_use(int(port), host):
        sys.stdout.write('using')
    else:
        sys.stdout.write('free')
