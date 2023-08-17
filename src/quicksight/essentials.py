"""
Module with essential functions for QuickSight API.
"""

from typing import Iterator

from botocore.exceptions import ClientError

###########################################
# Arn transformation functions
###########################################


def get_id_from_arn(arn: str) -> str:
    """Get ID from ARN.

    Args:
        arn (str): ARN.

    Returns:
        str: ID.
    """

    return arn.split("/")[-1]


def get_account_id_from_arn(arn: str) -> str:
    """Get account ID from ARN.

    Args:
        arn (str): ARN.

    Returns:
        str: Account ID.
    """

    return arn.split(":")[4]


def replace_account_id(arn: str, account_id: str) -> str:
    """Replace account ID in ARN.

    Args:
        arn (str): ARN.
        account_id (str): Account ID.

    Returns:
        str: ARN with replaced account ID.
    """

    return arn.replace(get_account_id_from_arn(arn), account_id)


###########################################
# General functions
###########################################


def find_assets(
    account_id: str,
    search_fn: callable,
    filters: dict[str, str],
    lookup_field: str,
) -> list[dict]:
    """Find an assets by filter criteria.

    Args:
        account_id (str): AWS account id.
        search_fn (callable): QuickSight search function.
        filters (dict[str, str]): Search filters.
        lookup_field (str): Field in response to lookup.

    Returns:
        list[dict]: Assets found.
    """

    params = {
        "AwsAccountId": account_id,
        "Filters": filters,
        "MaxResults": 10,
    }

    response: dict = search_fn(**params)

    status: int = response.get("Status", 0)
    if (status < 200) or (status >= 300):
        raise ValueError(f"Request failed with status {status}.\n{response}")

    if len(response.get(lookup_field, [])) == 0:
        raise ValueError(f"No assets found for filters\n{filters}")

    return response[lookup_field]


def describe_asset(
    account_id: str,
    describe_fn: callable,
    params: dict[str, str],
    lookup_field: str = None,
) -> dict:
    """Describe an asset.

    Args:
        account_id (str): AWS account id.
        describe_fn (callable): QuickSight describe function.
        asset_id (dict[str, str]): pair of Asset ID name and value.

    Returns:
        dict: Asset information.
    """

    response = describe_fn(AwsAccountId=account_id, **params)

    if 200 <= response.get("Status", 0) < 300:
        return response.get(lookup_field) if lookup_field else response
    else:
        raise ValueError(response)


def get_asset_ids_from_definition(
    definitions: list[dict],
    arn_key: str = "Arn",
) -> Iterator[str]:
    """Get assets IDs from definitions with Arn.

    Args:
        definitions (list[dict]): Asset definition.
        arn_key (str, optional): Key in definition to get ARN. Defaults to "Arn".

    Yields:
        Iterator[str]: IDs.
    """

    for dataset in definitions:
        if arn_key not in dataset:
            raise IndexError(f"Key {arn_key} not found in {dataset}")

        yield get_id_from_arn(dataset[arn_key])


###########################################
# Functions to find asset ids in QuickSight
###########################################


def find_asset_ids(
    account_id: str,
    search_fn: callable,
    filters: dict[str, str],
    lookup_field: str,
    id_key: str,
) -> list[str]:
    """
    Find an assets by filter criteria.

    Args:
        account_id (str): AWS account id.
        search_fn (callable): QuickSight search function.
        filters (dict[str, str]): Search filters.
        lookup_field (str): Field in response to lookup.
        id_key (str): Key in response to get ID.

    Returns:
        list[str]: ids of assets found.
    """

    return [
        asset.get(id_key)
        for asset in find_assets(
            account_id=account_id,
            search_fn=search_fn,
            filters=filters,
            lookup_field=lookup_field,
        )
    ]


def find_asset_id(
    account_id: str,
    search_fn: callable,
    filters: dict[str, str],
    lookup_field: str,
    id_key: str,
) -> str:
    """
    Find an asset by filter criteria.

    Raises ValueError if multiple assets found.

    Args:
        account_id (str): AWS account id.
        search_fn (callable): QuickSight search function.
        filters (dict[str, str]): Search filters.
        lookup_field (str): Field in response to lookup.
        id_key (str): Key in response to get ID.

    Returns:
        str: id of asset found.
    """

    ids = find_asset_ids(
        account_id=account_id,
        search_fn=search_fn,
        filters=filters,
        lookup_field=lookup_field,
        id_key=id_key,
    )

    if len(ids) > 1:
        raise ValueError(f"Multiple assets found for filters {filters}.\n{ids}")

    return ids[0]


##################################################
# Function to create or update asset in QuickSight
##################################################
def create_or_update_asset(
    params: dict, create_fn: callable, update_fn: callable
) -> dict:
    """
    Create or update QuickSight asset.

    Args:
        params (dict): Parameters for create or update function.
        create_fn (callable): QuickSight create function.
        update_fn (callable): QuickSight update function.

    Returns:
        dict: Response from create or update function.
    """
    try:
        response: dict = create_fn(**params)
    except ClientError as err:
        if err.response["Error"]["Code"] == "ResourceExistsException":
            print("\tresource already exists. Updating...")
            # for datasource we need to remove permissions and type
            params.pop("Permissions")
            if "Type" in params:
                params.pop("Type")
            response: dict = update_fn(**params)
        else:
            raise err

    status: int = response.get("Status", 0)
    if (status < 200) or (status >= 300):
        raise ValueError(f"Request failed with status {status}.\n{response}")

    return response
