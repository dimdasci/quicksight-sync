"""
CLI Entry point for the QuickSight Sync tool
"""
import click

from src.cli import export_cli, import_cli


@click.group()
def main():
    pass


@main.command()
@click.option(
    "--profile",
    "-p",
    type=click.Choice(["dev", "qa", "staging", "prod"], case_sensitive=True),
    default="dev",
    show_default=True,
    help="AWS Profile to export from",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, writable=True, readable=True
    ),
    default=".",
    show_default=True,
    help="Output directory",
)
@click.argument("analysis_id", nargs=1, required=True)
def get(profile: str, output: str, analysis_id: str):
    """
    Export QuickSight assets for analysis from AWS to local directory
    """
    export_cli(profile, output, analysis_id)


@main.command()
@click.option(
    "--profile",
    "-p",
    type=click.Choice(["dev", "qa", "staging", "prod"], case_sensitive=True),
    required=True,
    help="AWS Profile to import assets",
)
@click.argument(
    "dump",
    type=click.File("r"),
)
def put(profile: str, dump: str):
    """
    Imports QuickSight assets from a local dump file to AWS
    """
    import_cli(profile, dump)


if __name__ == "__main__":
    main()
