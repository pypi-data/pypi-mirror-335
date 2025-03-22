import boto3
from artd_customer.models import Customer
from artd_channels.models import Credential, Channel, Provider, Messagge


def send_otp_via_sms(message: str, customer_id: int) -> dict:
    """
    Sends an OTP (One Time Password) via SMS to a customer's phone number using AWS SNS.

    This function retrieves the customer's phone number and credentials for SMS services from
    the database and sends an OTP via AWS SNS.

    Args:
        message (str): The OTP message to be sent.
        customer_id (int): The ID of the customer to whom the OTP will be sent.

    Returns:
        dict: The response from AWS SNS containing details about the sent message.

    Raises:
        Customer.DoesNotExist: If no customer is found with the given `customer_id`.
        Credential.DoesNotExist: If no credential is found for the SMS channel and AWS provider.
        Exception: If an error occurs while sending the message or creating the Messagge record.
    """

    # Retrieve the customer using the provided customer ID
    customer_instance = Customer.objects.get(id=customer_id)
    phone_number = customer_instance.phone

    # Retrieve the Channel and Provider instances
    channel_instance = Channel.objects.get(name="SMS")
    provider_instance = Provider.objects.get(name="Aws")

    # Fetch the corresponding credentials from the Credential model
    credential_instance = Credential.objects.get(
        channel=channel_instance, provider=provider_instance
    )
    credentials_dict = credential_instance.credentials

    # Extract AWS credentials and other required details
    aws_access_key_id = credentials_dict.get("aws_access_key_id")
    aws_secret_access_key = credentials_dict.get("aws_secret_access_key")
    aws_region = credentials_dict.get("aws_region")

    # Set up the AWS SNS client
    sns_client = boto3.client(
        "sns",
        region_name=aws_region,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    try:
        # Send the OTP message via AWS SNS
        response = sns_client.publish(
            PhoneNumber=phone_number,
            Message=message,
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

        return response
    except Customer.DoesNotExist:
        print(f"Customer with ID {customer_id} not found.")
        raise
    except Credential.DoesNotExist:
        print("SMS credentials not found for the AWS provider.")
        raise
    except Exception as e:
        print(f"Error sending SMS or logging message: {e}")
        raise
