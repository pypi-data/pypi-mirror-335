import boto3
from artd_customer.models import Customer
from artd_channels.models import Credential, Channel, Provider, Messagge
from botocore.exceptions import NoCredentialsError, ClientError


def send_email(subject: str, message: str, customer_id: int) -> bool:
    """
    Sends an email using AWS SES (Simple Email Service).

    This function retrieves email credentials from the database and sends
    an email via AWS SES using the provided subject, message, and recipient.

    Args:
        subject (str): The subject of the email.
        message (str): The content of the email message.
        to_email (str): The recipient's email address.

    Returns:
        bool: Returns `True` if the email is sent successfully, otherwise `False`.

    Raises:
        Exception: If the required credentials or resources are not found.
        NoCredentialsError: If AWS credentials are not available.
        ClientError: If there is an error with the AWS SES client during the email sending process.
    """
    # Retrieve the customer using the provided customer ID
    customer_instance = Customer.objects.get(id=customer_id)
    customer_email = customer_instance.email

    # Retrieve the Channel and Provider instances
    channel_instance = Channel.objects.get(name="Email")
    provider_instance = Provider.objects.get(name="Aws")

    # Fetch the corresponding credentials from the Credential model
    credential_instance = Credential.objects.get(
        channel=channel_instance, provider=provider_instance
    )
    credentials_dict = credential_instance.credentials

    # Extract AWS credentials and other required details
    aws_access_key_id = credentials_dict.get("aws_access_key_id")
    aws_secret_access_key = credentials_dict.get("aws_secret_access_key")
    aws_from_email = credentials_dict.get("aws_from_email")
    aws_region = credentials_dict.get("aws_region")

    # Set up the AWS SES client
    ses_client = boto3.client(
        "ses",
        region_name=aws_region,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    try:
        # Send the email using AWS SES
        response = ses_client.send_email(
            Source=aws_from_email,
            Destination={"ToAddresses": [customer_email]},
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {
                    "Text": {"Data": message, "Charset": "UTF-8"},
                },
            },
        )
        # Log the message in the Messagge model, storing the response
        Messagge.objects.create(
            messages=message,
            channel=channel_instance,
            provider=provider_instance,
            customer=customer_instance,
            result=response,  # Store the AWS SNS response
            retries=0,  # Initial retry count set to 0
        )
        print(response)
        return True
    except NoCredentialsError:
        print("Error: AWS credentials not available")
        return False
    except ClientError as e:
        print(f"Error sending email: {e.response['Error']['Message']}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


def send_ses_email(subject: str, message: str, to_email: str) -> bool:
    """
    Wrapper function to send an email via AWS SES.

    Args:
        subject (str): The subject of the email.
        message (str): The content of the email message.
        to_email (str): The recipient's email address.

    Returns:
        bool: Returns `True` if the email is sent successfully, otherwise `False`.
    """
    return send_email(subject, message, to_email)
