"""Functions to export assets from QuickSight."""

from typing import Optional

import boto3

from src.quicksight.essentials import describe_asset, get_asset_ids_from_definition

#############################################
# Functions to get asset ids from definitions
#############################################


def get_analysis_dataset_ids(analysis_definition: dict) -> set[str]:
    """Get analysis dataset IDs from analysis definitions.

    Args:
        analysis_definitions (dict): Analysis definition.

    Returns:
        set[str]: set of IDs.
    """

    return set(
        get_asset_ids_from_definition(
            analysis_definition.get("Definition").get("DataSetIdentifierDeclarations"),
            "DataSetArn",
        )
    )


def get_rls_dataset_ids(dataset_definitions: list[dict]) -> set[str]:
    """Get RLS dataset IDs from dataset definitions.

    Args:
        dataset_definitions (dict): Asset definition.

    Returns:
        set[str]: set of IDs.
    """

    # Get RowLevelPermissionDataSet definitions from analysis definition
    rls_dataset_definitions = [
        ds.get("RowLevelPermissionDataSet")
        for ds in dataset_definitions
        if "RowLevelPermissionDataSet" in ds
    ]

    # if there is no RLS datasets, return empty set
    if len(rls_dataset_definitions) == 0:
        return set()

    return set(
        get_asset_ids_from_definition(
            rls_dataset_definitions,
            "Arn",
        )
    )


def get_datasource_ids(dataset_definitions: list[dict]) -> set[str]:
    """Get datasource IDs from dataset definitions.

    Args:
        dataset_definitions (dict): Asset definition.

    Returns:
        set[str]: set of IDs.
    """

    # Get datasource references from dataset definitions
    datasorce_references: list[dict] = [
        ref.get("RelationalTable")
        for ds in dataset_definitions
        for ref in ds.get("PhysicalTableMap", {}).values()
        if "RelationalTable" in ref
    ]

    if len(datasorce_references) == 0:
        return set()

    return set(get_asset_ids_from_definition(datasorce_references, "DataSourceArn"))


####################################
# Functions to get asset definitions
####################################


def get_analysis_definition(
    account_id: str,
    analysis_id: str,
    qs_client: boto3.client,
) -> dict:
    """Get analysis definition.

    Args:
        account_id (str): AWS account id.
        analysis_id (str): Analysis id.
        qs_client (boto3.client): QuickSight client.

    Returns:
        dict: Analysis definition.
    """

    return describe_asset(
        account_id=account_id,
        describe_fn=qs_client.describe_analysis_definition,
        params={"AnalysisId": analysis_id},
    )


def get_analysis_permissions(
    account_id: str,
    analysis_id: str,
    qs_client: boto3.client,
) -> dict:
    """Get analysis permissions definition.

    Args:
        account_id (str): AWS account id.
        analysis_id (str): Analysis id.
        qs_client (boto3.client): QuickSight client.

    Returns:
        dict: Analysis permissions.
    """

    return describe_asset(
        account_id=account_id,
        describe_fn=qs_client.describe_analysis_permissions,
        params={"AnalysisId": analysis_id},
        lookup_field="Permissions",
    )


def get_dataset_definition(
    account_id: str,
    dataset_id: str,
    qs_client: boto3.client,
) -> dict:
    """Get dataset definition.

    Args:
        account_id (str): AWS account id.
        dataset_id (str): Dataset id.
        qs_client (boto3.client): QuickSight client.

    Returns:
        dict: Dataset definition.
    """

    return describe_asset(
        account_id=account_id,
        describe_fn=qs_client.describe_data_set,
        params={"DataSetId": dataset_id},
        lookup_field="DataSet",
    )


def get_dataset_permissions(
    account_id: str,
    dataset_id: str,
    qs_client: boto3.client,
) -> dict:
    """Get dataset permissions definition.

    Args:
        account_id (str): AWS account id.
        dataset_id (str): Dataset id.
        qs_client (boto3.client): QuickSight client.

    Returns:
        dict: Dataset permissions.
    """

    return describe_asset(
        account_id=account_id,
        describe_fn=qs_client.describe_data_set_permissions,
        params={"DataSetId": dataset_id},
        lookup_field="Permissions",
    )


def get_datasource_definition(
    account_id: str,
    datasource_id: str,
    qs_client: boto3.client,
) -> dict:
    """Get datasource definition.

    Args:
        account_id (str): AWS account id.
        datasource_id (str): Datasource id.
        qs_client (boto3.client): QuickSight client.

    Returns:
        dict: Datasource definition.
    """

    return describe_asset(
        account_id=account_id,
        describe_fn=qs_client.describe_data_source,
        params={"DataSourceId": datasource_id},
        lookup_field="DataSource",
    )


def get_datasource_permissions(
    account_id: str,
    datasource_id: str,
    qs_client: boto3.client,
) -> dict:
    """Get datasource permissions definition.

    Args:
        account_id (str): AWS account id.
        datasource_id (str): Datasource id.
        qs_client (boto3.client): QuickSight client.

    Returns:
        dict: Datasource permissions.
    """

    return describe_asset(
        account_id=account_id,
        describe_fn=qs_client.describe_data_source_permissions,
        params={"DataSourceId": datasource_id},
        lookup_field="Permissions",
    )


#####################################################
# Functions to dump asset definitions from QuickSight
#####################################################


def dump_analysis(definition: dict, permissions: Optional[dict] = None) -> dict:
    return {
        "AnalysisId": definition["AnalysisId"],
        "Name": definition["Name"],
        "Definition": definition["Definition"],
        "Permissions": permissions,
    }


def dump_dataset(definition: dict, permissions: Optional[dict] = None) -> dict:
    return {
        "DataSetId": definition["DataSetId"],
        "Name": definition["Name"],
        "PhysicalTableMap": definition["PhysicalTableMap"],
        "LogicalTableMap": definition["LogicalTableMap"],
        "OutputColumns": definition["OutputColumns"],
        "ImportMode": definition["ImportMode"],
        "Permissions": permissions,
        "RowLevelPermissionDataSet": definition.get("RowLevelPermissionDataSet"),
        "DataSetUsageConfiguration": definition.get("DataSetUsageConfiguration"),
    }


def dump_data_source(definition: dict, permissions: Optional[dict] = None) -> dict:
    return {
        "DataSourceId": definition["DataSourceId"],
        "Name": definition["Name"],
        "Type": definition["Type"],
        "DataSourceParameters": definition["DataSourceParameters"],
        "Credentials": None,
        "Permissions": permissions,
        "VpcConnectionProperties": definition.get("VpcConnectionProperties"),
        "SslProperties": definition.get("SslProperties"),
        "ErrorInfo": definition.get("ErrorInfo"),
    }


#############################################################
# Main function to dump QuickSight assets related to analysis
#############################################################
def get_dump(account_id: str, qs_client: boto3.client, analysis_id: str) -> dict:
    """Get QuickSight assets dump to reproduce analysis.

    For analysis id we get analysis definition.
    From it we get dataset ids and dataset definitions.
    Datasets can have references to other datasets for Row level security.
    We get those datasets ids and then definitions as well.
    Finally we get datasource ids from all dataset definitions and
    get datasource definitions.

    All data is returned as a dict with keys:
    - analysis
    - datasets
    - datasources

    Args:
        account_id (str): AWS account id.
        qs_client (boto3.client): QuickSight client.
        analysis_id (str): Analysis Id.

    Returns:
        dict: QuickSight assets dump.
    """

    if account_id is None:
        raise ValueError("account_id is required")

    if qs_client is None:
        raise ValueError("qs_client is required")

    if analysis_id is None:
        raise ValueError("analysis_id is required")

    # Get analysis definition and permissions
    analysis_definition: dict = get_analysis_definition(
        account_id=account_id, analysis_id=analysis_id, qs_client=qs_client
    )

    analysis_permissions: dict = get_analysis_permissions(
        account_id=account_id, analysis_id=analysis_id, qs_client=qs_client
    )

    # Get unique dataset IDs from analysis definition
    analysis_dataset_ids: set[str] = get_analysis_dataset_ids(analysis_definition)

    # Get analysis datasets definitions
    analysis_dataset_definitions: list[dict] = [
        {
            "definition": get_dataset_definition(
                account_id=account_id,
                qs_client=qs_client,
                dataset_id=id,
            ),
            "permissions": get_dataset_permissions(
                account_id=account_id,
                qs_client=qs_client,
                dataset_id=id,
            ),
        }
        for id in analysis_dataset_ids
    ]

    # Get unique RLS dataset IDs from analysis dataset definitions
    rls_dataset_ids: set[str] = get_rls_dataset_ids(analysis_dataset_definitions)

    # Get row level security dataset definitions
    rls_dataset_definitions: list[dict] = [
        {
            "definition": get_dataset_definition(
                account_id=account_id,
                qs_client=qs_client,
                dataset_id=id,
            ),
            "permissions": get_dataset_permissions(
                account_id=account_id,
                qs_client=qs_client,
                dataset_id=id,
            ),
        }
        for id in rls_dataset_ids
    ]

    # Get unique datasource IDs from datasets
    datasource_ids: set[dict] = get_datasource_ids(
        row["definition"]
        for row in analysis_dataset_definitions + rls_dataset_definitions
    )

    # Get datasource definitions
    datasource_definitions: list[dict] = [
        {
            "definition": get_datasource_definition(
                account_id=account_id,
                qs_client=qs_client,
                datasource_id=id,
            ),
            "permissions": get_datasource_permissions(
                account_id=account_id,
                qs_client=qs_client,
                datasource_id=id,
            ),
        }
        for id in datasource_ids
    ]

    # return assets dump
    return {
        "analysis": dump_analysis(
            definition=analysis_definition, permissions=analysis_permissions
        ),
        "analysis_datasets": [
            dump_dataset(
                definition=dataset["definition"], permissions=dataset["permissions"]
            )
            for dataset in analysis_dataset_definitions
        ],
        "security_datasets": [
            dump_dataset(
                definition=dataset["definition"], permissions=dataset["permissions"]
            )
            for dataset in rls_dataset_definitions
        ],
        "datasources": [
            dump_data_source(
                definition=datasource["definition"],
                permissions=datasource["permissions"],
            )
            for datasource in datasource_definitions
        ],
    }
