import requests
import json
import base64
from artd_customer.models import Customer
from artd_channels.models import (
    Channel,
    Provider,
    Credential,
    Messagge,
)  # Asegúrate de que estén bien importados tus modelos


def send_sms(message: str, customer_id: int) -> str:
    """
    Sends an SMS message to a customer's phone number using the Labsmobile API.

    Args:
        message (str): The SMS message content to be sent.
        customer_id (int): The ID of the customer to whom the message will be sent.

    Returns:
        str: The response text from the Labsmobile API after sending the SMS.

    Raises:
        Customer.DoesNotExist: If no customer is found with the given customer_id.
        Channel.DoesNotExist: If the 'SMS' channel is not found.
        Provider.DoesNotExist: If the 'Labsmobile' provider is not found.
        Credential.DoesNotExist: If the credentials for the 'SMS' channel and 'Labsmobile' provider are not found.
    """
    # Fetch the customer using the customer_id
    customer_instance = Customer.objects.get(id=customer_id)
    phone_number = customer_instance.phone

    # Fetch the 'SMS' channel and 'Labsmobile' provider instances
    channel_instance = Channel.objects.get(name="SMS")
    provider_instance = Provider.objects.get(name="Labsmobile")

    # Fetch the credentials for the given channel and provider
    credential_instance = Credential.objects.get(
        channel=channel_instance, provider=provider_instance
    )
    credentials_dict = credential_instance.credentials

    # Extract username and token from credentials
    labs_mobile_username = credentials_dict.get("labs_mobile_username")
    labs_mobile_token = credentials_dict.get("labs_mobile_token")

    # Create the basic authentication token for Labsmobile
    user_token = f"{labs_mobile_username}:{labs_mobile_token}"
    credentials = base64.b64encode(user_token.encode()).decode()

    # Labsmobile API URL
    url = "https://api.labsmobile.com/json/send"

    # Prepare the payload for the POST request
    payload = json.dumps(
        {
            "message": message,
            "tpoa": "Sender",  # Sender identification
            "recipient": [{"msisdn": phone_number}],  # Recipient's phone number
        }
    )

    # Headers for the request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {credentials}",
        "Cache-Control": "no-cache",
    }

    # Make the POST request to Labsmobile API
    response = requests.post(url, headers=headers, data=payload)

    # Print the response from the API (for debugging purposes)
    print(response.text)

    # Store the message and response in the database
    Messagge.objects.create(
        messages=message,
        channel=channel_instance,
        provider=provider_instance,
        customer=customer_instance,
        result=response.json()
        if response.content
        else {},  # Save the response as JSON or empty dict
        retries=0,  # Initialize retries as 0
    )

    # Return the API response text
    return response.text
