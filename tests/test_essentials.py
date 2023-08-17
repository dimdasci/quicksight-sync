from unittest.mock import Mock

from src.quicksight.essentials import (
    describe_asset,
    find_assets,
    get_asset_ids_from_definition,
    get_id_from_arn,
)

# Mocking Boto3 client
boto3_client = Mock()

###########################################
# General functions
###########################################


def test_find_assets():
    # Define a mock response from QuickSight
    mock_response = {
        "Status": 200,
        "Assets": [{"Name": "Asset1", "Id": "1"}, {"Name": "Asset2", "Id": "2"}],
    }

    # Mock the search function
    boto3_client.search_fn.return_value = mock_response

    # Call the function being tested
    result = find_assets(
        "account_id", boto3_client.search_fn, {"key": "value"}, "Assets"
    )

    # Assertion
    assert result == [{"Name": "Asset1", "Id": "1"}, {"Name": "Asset2", "Id": "2"}]
    boto3_client.search_fn.assert_called_once_with(
        AwsAccountId="account_id", Filters={"key": "value"}, MaxResults=10
    )


def test_describe_asset_with_lookup():
    # Define a mock response from QuickSight
    mock_response = {"Status": 200, "Asset": {"Name": "Asset1", "Id": "1"}}

    # Mock the describe function
    boto3_client.describe_fn_lookup.return_value = mock_response

    # Call the function being tested
    result = describe_asset(
        account_id="account_id",
        describe_fn=boto3_client.describe_fn_lookup,
        params={"argument": "value"},
        lookup_field="Asset",
    )

    # Assertion
    assert result == {"Name": "Asset1", "Id": "1"}
    boto3_client.describe_fn_lookup.assert_called_once_with(
        AwsAccountId="account_id", argument="value"
    )


def test_describe_asset_wo_lookup():
    # Define a mock response from QuickSight
    mock_response = {"Status": 200, "Asset": {"Name": "Asset1", "Id": "1"}}

    # Mock the describe function
    boto3_client.describe_fn_no_lookup.return_value = mock_response

    # Call the function being tested
    result = describe_asset(
        account_id="account_id",
        describe_fn=boto3_client.describe_fn_no_lookup,
        params={"argument": "value"},
    )

    # Assertion
    assert result == {"Status": 200, "Asset": {"Name": "Asset1", "Id": "1"}}
    boto3_client.describe_fn_no_lookup.assert_called_once_with(
        AwsAccountId="account_id", argument="value"
    )


def test_get_id_from_arn():
    # Call the function being tested
    result = get_id_from_arn("arn:aws:quicksight:region:account:asset/123")

    # Assertion
    assert result == "123"


def test_get_asset_ids_from_definition():
    # Define a mock list of asset definitions
    mock_definitions = [{"Arn": "arn1"}, {"Arn": "arn2"}]

    # Call the function being tested
    result = list(get_asset_ids_from_definition(mock_definitions, "Arn"))

    # Assertion
    assert result == ["arn1", "arn2"]
