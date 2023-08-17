from unittest.mock import Mock

from src.quicksight.aws_config import get_aws_account_id


def test_get_aws_account_id():
    # Mock the GetCallerIdentity response
    session = Mock()
    client = Mock()

    mock_response = {"Account": "123456789012"}
    client.get_caller_identity.return_value = mock_response
    session.client.return_value = client

    # Call the function with mock session and client
    account_id = get_aws_account_id(session)

    # Assert that the function returns the expected account ID
    assert account_id == "123456789012"


# Test case where account ID is not retrieved
def test_missing_account_id():
    # Mock the GetCallerIdentity response with missing Account key
    session = Mock()
    client = Mock()

    mock_response = {}
    client.get_caller_identity.return_value = mock_response
    session.client.return_value = client

    # Call the function with mock session and client
    account_id = get_aws_account_id(session)

    # Assert that the function returns None
    assert account_id is None
