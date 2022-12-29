"""Command-line interface."""
import click


@click.command()
@click.version_option()
def run() -> None:
    """brightway_projects."""
    pass


if __name__ == "__main__":
    run(prog_name="brightway_projects")  # pragma: no cover
