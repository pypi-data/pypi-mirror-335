import typer
import psycopg


def setup_database(admin_config, db_name, db_user, db_password):
    conn_string = f"host={admin_config['host']} port={admin_config['port']} user={admin_config['user']} password={admin_config['password']}"

    with psycopg.connect(conn_string, autocommit=True) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            db_exists = cursor.fetchone()

            if not db_exists:
                typer.echo(f"Creating database '{db_name}'...")
                cursor.execute(f"CREATE DATABASE {db_name}")
                typer.echo(f"Database '{db_name}' created successfully!")
            else:
                typer.echo(f"Database '{db_name}' already exists.")

            cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (db_user,))
            user_exists = cursor.fetchone()

            if not user_exists:
                typer.echo(f"Creating user '{db_user}'...")
                cursor.execute(f'CREATE USER "{db_user}" WITH PASSWORD \'{db_password}\'')
                typer.echo(f"User '{db_user}' created successfully!")
            else:
                typer.echo(f"User '{db_user}' already exists.")
                typer.echo(f"Updating password for user '{db_user}'...")
                cursor.execute("ALTER USER %s WITH PASSWORD %s", (db_user, db_password))

            typer.echo(f"Granting privileges on '{db_name}' to '{db_user}'...")
            cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user}")

    db_conn_string = f"{conn_string} dbname={db_name}"

    with psycopg.connect(db_conn_string, autocommit=True) as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"GRANT ALL ON SCHEMA public TO {db_user}")
            typer.echo(f"Schema privileges granted to '{db_user}'!")

    typer.echo("Database setup completed successfully!")
