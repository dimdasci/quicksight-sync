"""
Functions to import assets to QuickSight.
"""

import boto3

from src.quicksight.essentials import create_or_update_asset, get_id_from_arn

IMPORT_SUFFIX: str = "-imported"

#############################################
# Datasource import functions
#############################################


def prepare_datasource_definition(account_id: str, datasource: dict) -> dict:
    definition: dict = {
        key: value for key, value in datasource.items() if value is not None
    }

    definition.update(Name=datasource["Name"] + IMPORT_SUFFIX, AwsAccountId=account_id)

    return definition


def import_datasource(qs_client: boto3.client, datasource: dict) -> list[dict]:

    print(f"Importing datasource {datasource['Name']}...")

    original_datasource_id: str = datasource["DataSourceId"]
    target_datasource_id: str = datasource["DataSourceId"] + IMPORT_SUFFIX

    params = datasource.copy()
    params.update(
        DataSourceId=target_datasource_id,
    )

    response = create_or_update_asset(
        params=params,
        create_fn=qs_client.create_data_source,
        update_fn=qs_client.update_data_source,
    )

    return {
        "name": datasource["Name"],
        "arn": response["Arn"],
        "new_id": response["DataSourceId"],
        "org_id": original_datasource_id,
    }


def import_datasources(
    account_id: str, qs_client: boto3.client, datasources: list[dict]
) -> list[dict]:

    return [
        import_datasource(
            qs_client=qs_client,
            datasource=prepare_datasource_definition(
                account_id=account_id, datasource=ds
            ),
        )
        for ds in datasources
    ]


#############################################
# Dataset import functions
#############################################


def prepare_dataset_definition(
    account_id: str, dataset: dict, datasource_id_map: dict, dataset_id_map: dict
) -> dict:
    definition: dict = {
        key: value
        for key, value in dataset.items()
        if (key != "OutputColumns") and (value is not None)
    }

    definition.update(
        Name=dataset["Name"] + IMPORT_SUFFIX,
        AwsAccountId=account_id,
    )

    # Replace datasource old arn with new arn in PhysicalTableMap
    for table in definition["PhysicalTableMap"].values():
        table["RelationalTable"]["DataSourceArn"] = datasource_id_map[
            get_id_from_arn(table["RelationalTable"]["DataSourceArn"])
        ]

    # Replace dataset old arn with new arn in RowLevelPermissionDataSet
    if ("RowLevelPermissionDataSet" in definition) and (
        "Arn" in definition["RowLevelPermissionDataSet"]
    ):
        definition["RowLevelPermissionDataSet"]["Arn"] = dataset_id_map[
            get_id_from_arn(definition["RowLevelPermissionDataSet"]["Arn"])
        ]

    return definition


def import_dataset(
    qs_client: boto3.client,
    dataset: dict,
) -> list[dict]:

    print(f"Importing dataset {dataset['Name']}...")
    original_dataset_id: str = dataset["DataSetId"]
    target_dataset_id: str = dataset["DataSetId"] + IMPORT_SUFFIX

    # Remove None values from dataset
    dataset.update(
        DataSetId=target_dataset_id,
    )

    response = create_or_update_asset(
        params=dataset,
        create_fn=qs_client.create_data_set,
        update_fn=qs_client.update_data_set,
    )

    return {
        "name": dataset["Name"],
        "arn": response["Arn"],
        "new_id": response["DataSetId"],
        "org_id": original_dataset_id,
        "ingestion_id": response.get("IngestionId"),
        "ingestion_arn": response.get("IngestionArn"),
    }


def import_datasets(
    account_id: str,
    qs_client: boto3.client,
    datasets: list,
    datasource_id_map: dict,
    dataset_id_map: dict,
) -> list[dict]:

    return [
        import_dataset(
            qs_client=qs_client,
            dataset=prepare_dataset_definition(
                account_id=account_id,
                dataset=ds,
                datasource_id_map=datasource_id_map,
                dataset_id_map=dataset_id_map,
            ),
        )
        for ds in datasets
    ]


def prepare_analysis_definition(
    account_id: str,
    dataset_id_map: dict,
    analysis: dict,
) -> dict:
    """
    Prepare analysis definition for import

    Args:
        account_id (str): AWS account ID
        dataset_id_map (dict): Map of old dataset IDs to new dataset IDs
        analysis (dict): Analysis definition

    Returns:
        dict: Prepared analysis definition
    """

    target_analysis_name: str = analysis["Name"] + "-imported"
    target_analysis_id: str = analysis["AnalysisId"] + "-imported"

    definition = analysis.copy()
    definition.update(
        Name=target_analysis_name,
        AnalysisId=target_analysis_id,
        AwsAccountId=account_id,
    )

    # replace datasets arn with new arn
    for ds in definition["Definition"].get("DataSetIdentifierDeclarations"):
        ds["DataSetArn"] = dataset_id_map[get_id_from_arn(ds["DataSetArn"])]

    return definition


def import_analysis(qs_client: boto3.client, analysis: dict) -> dict:

    print(f"Importing analysis {analysis['Name']}...")

    response = create_or_update_asset(
        params=analysis,
        create_fn=qs_client.create_analysis,
        update_fn=qs_client.update_analysis,
    )

    return {
        "name": analysis["Name"],
        "arn": response["Arn"],
        "id": response["AnalysisId"],
    }


def get_dashboard_version(version_arn: str) -> int:
    """
    Extracts dashboard version from version ARN

    Args:
        version_arn (str): dashboard version ARN

    Returns:
        int: dashboard version"""

    return int(version_arn.split("/")[-1])


def prepare_dashboard_definition(
    account_id: str,
    analysis: dict,
) -> dict:
    """
    Prepare dashboard definition for import

    Args:
        account_id (str): AWS account id
        analysis (dict): original dashboard definition

    Returns:
        dict: prepared dashboard definition
    """

    definition = analysis.copy()

    # create dashboard name from analysis name
    id: str = definition.pop("AnalysisId") + "_dashboard"
    name: str = definition.pop("Name") + "_dashboard"

    definition.update(
        AwsAccountId=account_id,
        Name=name,
        DashboardId=id,
        DashboardPublishOptions={
            "AdHocFilteringOption": {"AvailabilityStatus": "DISABLED"},
            "ExportToCSVOption": {"AvailabilityStatus": "ENABLED"},
            "SheetControlsOption": {"VisibilityState": "COLLAPSED"},
            "SheetLayoutElementMaximizationOption": {"AvailabilityStatus": "ENABLED"},
            "VisualMenuOption": {"AvailabilityStatus": "ENABLED"},
            "VisualAxisSortOption": {"AvailabilityStatus": "ENABLED"},
            "ExportWithHiddenFieldsOption": {"AvailabilityStatus": "DISABLED"},
            "DataPointDrillUpDownOption": {"AvailabilityStatus": "ENABLED"},
            "DataPointMenuLabelOption": {"AvailabilityStatus": "ENABLED"},
            "DataPointTooltipOption": {"AvailabilityStatus": "ENABLED"},
        },
    )
    definition["Permissions"] = [
        {
            "Principal": "arn:aws:quicksight:us-east-1:157367673944:group/default/Reporting_management",
            "Actions": [
                "quicksight:DescribeDashboard",
                "quicksight:QueryDashboard",
                "quicksight:ListDashboardVersions",
            ],
        },
        {
            "Principal": "arn:aws:quicksight:us-east-1:157367673944:user/default/dmitrii.kharitonov+dev@vindow.com",
            "Actions": [
                "quicksight:DescribeDashboard",
                "quicksight:ListDashboardVersions",
                "quicksight:UpdateDashboardPermissions",
                "quicksight:QueryDashboard",
                "quicksight:UpdateDashboard",
                "quicksight:DeleteDashboard",
                "quicksight:UpdateDashboardPublishedVersion",
                "quicksight:DescribeDashboardPermissions",
            ],
        },
    ]

    return definition


def import_dashboard(account_id: str, qs_client: boto3.client, dashboard: dict) -> dict:
    """
    Import dashboard from dump file to AWS

    Args:
        account_id (str): AWS account ID
        qs_client (boto3.client): QuickSight client
        dashboard (dict): Dashboard definition

    Returns:
        dict: Imported dashboard metadata
    """
    # create or update dashboard
    response: dict = create_or_update_asset(
        params=dashboard,
        create_fn=qs_client.create_dashboard,
        update_fn=qs_client.update_dashboard,
    )

    # publish new version of dashboard
    version: int = get_dashboard_version(response["VersionArn"])
    publish_response: dict = qs_client.update_dashboard_published_version(
        AwsAccountId=account_id,
        DashboardId=response["DashboardId"],
        VersionNumber=version,
    )

    print(
        (
            f"Published dashboard {dashboard['DashboardId']}.v{version}... "
            + f"{publish_response['Status']}"
        )
    )
    return {
        "id": response["DashboardId"],
        "arn": response["Arn"],
        "version": version,
        "publish_status": publish_response["Status"],
    }


###############################################################
# Main function to import QuickSight assets related to analysis
###############################################################


def import_dump(account_id: str, qs_client: boto3.client, assets_dump: dict) -> dict:
    """
    Import QuickSight assets for analysis from dump file to AWS

    Args:
        account_id (str): Destination AWS account ID
        qs_client (boto3.client): QuickSight client
        assets_dump (dict): Analysis dump

    Returns:
        dict: Import results
    """

    if "datasources" not in assets_dump:
        raise ValueError("No datasources in dump file.")

    if "analysis_datasets" not in assets_dump:
        raise ValueError("No datasets in dump file.")

    if "analysis" not in assets_dump:
        raise ValueError("No analysis in dump file.")

    # import datasources
    datasources = import_datasources(
        account_id=account_id,
        qs_client=qs_client,
        datasources=assets_dump["datasources"],
    )

    # create a map of original datasource id to new datasource arn
    datasource_id_map = {ds["org_id"]: ds["arn"] for ds in datasources}

    # import datasets
    security_datasets = import_datasets(
        account_id=account_id,
        datasource_id_map=datasource_id_map,
        qs_client=qs_client,
        datasets=assets_dump["security_datasets"],
        dataset_id_map={},
    )

    dataset_id_map = {ds["org_id"]: ds["arn"] for ds in security_datasets}

    analysis_datasets = import_datasets(
        account_id=account_id,
        datasource_id_map=datasource_id_map,
        dataset_id_map=dataset_id_map,
        qs_client=qs_client,
        datasets=assets_dump["analysis_datasets"],
    )

    for ds in analysis_datasets:
        dataset_id_map[ds["org_id"]] = ds["arn"]

    # import analysis
    analysis_definition: dict = prepare_analysis_definition(
        account_id=account_id,
        dataset_id_map=dataset_id_map,
        analysis=assets_dump["analysis"],
    )

    analysis = import_analysis(
        qs_client=qs_client,
        analysis=analysis_definition,
    )

    # import dashboard
    dashboard_definition: dict = prepare_dashboard_definition(
        account_id=account_id,
        analysis=assets_dump["analysis"],
    )

    dashboard = import_dashboard(
        account_id=account_id,
        qs_client=qs_client,
        dashboard=dashboard_definition,
    )

    return {
        "target_account": account_id,
        "assets_dump": assets_dump,
        "datasources": datasources,
        "security_datasets": security_datasets,
        "analysis_datasets": analysis_datasets,
        "analysis": analysis,
        "dashboard": dashboard,
    }
