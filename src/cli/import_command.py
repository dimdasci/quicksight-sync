import json

import boto3

from src.quicksight.aws_config import get_aws_account_id
from src.quicksight.import_assets import import_dump


def import_cli(profile: str, dump: str) -> None:
    """
    Imports QuickSight assets from a JSON dump file.

    Args:
        profile: AWS profile to use.
        dump: Path to the JSON dump file.

    Returns:
        None
    """

    try:
        with dump as f:
            assets_dump = json.load(f)
    except ValueError as e:
        print(f"Can't read JSON file {dump}.")
        print(e)
        return

    # Create session for profile dev
    session = boto3.Session(profile_name=profile)

    ACCOUNT_ID: str = get_aws_account_id(boto_session=session)
    print(f"Importing QuickSight assets from {dump} to {ACCOUNT_ID}...")

    # create quicksight client
    qs = session.client("quicksight")

    try:
        results = import_dump(
            account_id=ACCOUNT_ID, qs_client=qs, assets_dump=assets_dump
        )
    except ValueError as e:
        print("Import failed.")
        print(e)
        return

    print("Imported:")
    for datasource in results["datasources"]:
        print(f"  - datasource\t\t{datasource['arn']}")
    for dataset in results["security_datasets"]:
        print(f"  - security dataset\t{dataset['arn']}")
    for dataset in results["analysis_datasets"]:
        print(f"  - analysis dataset\t{dataset['arn']}")
    print(f"  - analysis\t\t{results['analysis']['arn']}")
    print(
        (
            f"  - dashboard\t\t{results['dashboard']['arn']} "
            + f"v{results['dashboard']['version']}"
        )
    )
    print("Done.")
