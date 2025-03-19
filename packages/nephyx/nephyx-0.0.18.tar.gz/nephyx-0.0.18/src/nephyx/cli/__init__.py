import json
from pathlib import Path
import typer
from nephyx.utils.helper import import_app_entrypoint
import sys
import getpass

from nephyx.cli.postgres import setup_database

app = typer.Typer()


@app.command()
def init_db():
    db_host = "localhost"
    db_port = "5432"

    db_admin_user = typer.prompt("Enter database admin user")
    db_admin_password = getpass.getpass("Enter database admin password")

    # take from config
    db_name = typer.prompt("Enter database name")
    db_user = typer.prompt("Enter database user")
    db_password = getpass.getpass("Enter database password")

    admin_config = {
        "host": db_host,
        "port": db_port,
        "user": db_admin_user,
        "password": db_admin_password,
    }

    setup_database(admin_config, db_name, db_user, db_password)


@app.command()
def export_openapi():
    sys.path.insert(0, "")
    app = import_app_entrypoint()
    openapi = app.openapi()
    with Path("openapi.json").open("w") as f:
        json.dump(openapi, f, indent=2)


@app.command()
def run_dev(
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = True,
    app_dir: str = None
):
    import uvicorn

    typer.echo(f"Starting development server at http://{host}:{port}")
    uvicorn.run(
        "nephyx.core.app:get_app",
        host=host,
        port=port,
        reload=reload,
        factory=True
    )

#TODO run command
