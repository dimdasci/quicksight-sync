import json
from os import path

import boto3

from src.quicksight.aws_config import get_aws_account_id
from src.quicksight.export_assets import get_dump


def export_cli(profile: str, output: str, analysis_id: str) -> None:
    """
    Export QuickSight assets for analysis from AWS to local directory

    Args:
        profile: AWS profile to use
        output: directory to write output to
        analysis_id: QuickSight analysis ID to export

    Returns:
        None
    """

    # Create session for profile dev
    session = boto3.Session(profile_name=profile)

    ACCOUNT_ID: str = get_aws_account_id(boto_session=session)
    print(f"Exporting QuickSight assets for {ACCOUNT_ID}:analysis/{analysis_id}...")

    # create quicksight client
    qs = session.client("quicksight")

    try:
        assets_dump = get_dump(ACCOUNT_ID, qs, analysis_id)
    except ValueError as e:
        print("Export failed.")
        print(e)
        return

    # write to file in output directory with name <analysis_name>.json
    output_file = path.join(output, f"{analysis_id}.json")
    with open(output_file, "w") as f:
        f.write(json.dumps(assets_dump, indent=4))

    # print summary
    print(
        f"Found {len(assets_dump['analysis_datasets'])} analysis datasets,\n"
        f"      {len(assets_dump['security_datasets'])} security datasets,\n"
        f"  and {len(assets_dump['datasources'])} data sources."
    )
    print(f"Exported assets to {output_file}")
    print("Done.")
