"""Command-line interface."""
import click


@click.command()
@click.version_option()
def run() -> None:
    """bw_projects."""
    pass


if __name__ == "__main__":
    run(prog_name="bw_projects")  # pragma: no cover
