import boto3


def get_aws_account_id(boto_session: boto3.session.Session) -> str:
    """Get AWS account ID from profile.

    Args:
        profile_name (str): AWS profile name.
        boto_session (boto3.session.Session): Boto3 session.

    Returns:
        str: AWS account ID.
    """

    # Create an STS client using the provided profile
    sts_client = boto_session.client("sts")

    # Call the GetCallerIdentity API to retrieve the AWS account ID
    response = sts_client.get_caller_identity()
    account_id = response.get("Account", None)

    return account_id
