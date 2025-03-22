import requests
import json
from artd_customer.models import Customer
from artd_channels.models import (
    Credential,
    Channel,
    Provider,
    Messagge,
)  # Asegúrate de que esté bien importado el modelo


class Messagebird:
    """
    A class to interact with the Messagebird API for sending templated messages
    and fetching contact details.

    Attributes:
        __CHANNEL_NAME (str): The name of the messaging channel ('WhatsApp').
        __PROVIDER_NAME (str): The name of the provider ('Messagebird').
        __AUTH_HEADER_TEMPLATE (str): Template for the Authorization header.
        __CONTENT_TYPE_HEADER (str): Content type header for requests.
        __creadentials (None): Placeholder for credentials (not currently used).
    """

    __CHANNEL_NAME = "WhatsApp"
    __PROVIDER_NAME = "Messagebird"
    __AUTH_HEADER_TEMPLATE = "AccessKey {}"
    __CONTENT_TYPE_HEADER = "application/json"
    __creadentials = None

    def __init__(self, *args, **kwargs):
        """
        Initializes the Messagebird class, extracting credentials and API
        information from the Channel and Provider models.

        Attributes fetched:
            __workspace_id (str): The workspace ID from the credentials.
            __channel_id (str): The channel ID from the credentials.
            __access_key (str): The access key used for API authentication.
            __project_id (str): The project ID associated with the workspace.
            __base_url (str): The base URL for Messagebird API requests.
            __headers (dict): HTTP headers used for API requests.
        """
        self.__channel_instance = Channel.objects.get(name=self.__CHANNEL_NAME)
        self.__provider_instance = Provider.objects.get(name=self.__PROVIDER_NAME)
        credential_instance = Credential.objects.get(
            channel=self.__channel_instance, provider=self.__provider_instance
        )
        self.__credentials_dict = credential_instance.credentials

        self.__workspace_id = self.__credentials_dict.get("workspaceId")
        self.__channel_id = self.__credentials_dict.get("channelId")
        self.__access_key = self.__credentials_dict.get("AccessKey")
        self.__project_id = self.__credentials_dict.get("projectId")
        self.__project_id_close = self.__credentials_dict.get("projectIdClose")
        self.__project_id_image_otp = self.__credentials_dict.get("projectIdImageOTP")
        self.__base_url = self.__credentials_dict.get("url")

        self.__headers = {
            "Authorization": self.__AUTH_HEADER_TEMPLATE.format(self.__access_key),
            "Content-Type": self.__CONTENT_TYPE_HEADER,
        }
        print(self.__headers)

    def get_customer_phone(self, customer_id):
        """
        Fetches the phone number of a customer using their customer ID.

        Args:
            customer_id (int): The ID of the customer.

        Returns:
            str: The phone number of the customer.

        Raises:
            Exception: If the customer does not exist.
        """
        try:
            customer_instance = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            raise Exception("Customer not found")

        phone_number = customer_instance.phone
        return phone_number

    def send_template(self, customer_id, key, value):
        """
        Sends a templated message to a customer via the Messagebird API.

        Args:
            customer_id (int): The ID of the customer.
            key (str): The key in the template that will be replaced by the value.
            value (str): The value that will replace the key in the template.

        Returns:
            dict: JSON response from the Messagebird API after sending the message.
        """
        customer_instance = Customer.objects.get(id=customer_id)
        phone_number = self.get_customer_phone(customer_id)

        url = f"{self.__base_url}workspaces/{self.__workspace_id}/channels/{self.__channel_id}/messages"
        print(url)

        # Prepare the payload for the first message (template)
        payload = json.dumps(
            {
                "receiver": {
                    "contacts": [
                        {
                            "identifierKey": "phonenumber",
                            "identifierValue": phone_number,
                        }
                    ]
                },
                "template": {
                    "projectId": self.__project_id,
                    "version": "latest",
                    "locale": "es",
                    "parameters": [{"type": "string", "key": key, "value": value}],
                },
            }
        )
        print(payload)

        # Make the initial POST request to send the templated message
        response = requests.post(url, headers=self.__headers, data=payload)
        response_json = response.json()
        # Log the message in the Messagge model, storing the response
        Messagge.objects.create(
            messages=value,  # Assuming this is your message content
            channel=self.__channel_instance,
            provider=self.__provider_instance,
            customer=customer_instance,
            result=response_json,  # Store the response from MessageBird
            retries=0,  # Initial retry count set to 0
        )

        return response_json

    def send_template_close(self, customer_id, key, value):
        """
        Sends a templated message to a customer via the Messagebird API.

        Args:
            customer_id (int): The ID of the customer.
            key (str): The key in the template that will be replaced by the value.
            value (str): The value that will replace the key in the template.

        Returns:
            dict: JSON response from the Messagebird API after sending the message.
        """
        customer_instance = Customer.objects.get(id=customer_id)
        phone_number = self.get_customer_phone(customer_id)

        url = f"{self.__base_url}workspaces/{self.__workspace_id}/channels/{self.__channel_id}/messages"
        print(url)

        # Prepare the payload for the first message (template)
        payload = json.dumps(
            {
                "receiver": {
                    "contacts": [
                        {
                            "identifierKey": "phonenumber",
                            "identifierValue": phone_number,
                        }
                    ]
                },
                "template": {
                    "projectId": self.__project_id_close,
                    "version": "latest",
                    "locale": "es",
                    "parameters": [{"type": "string", "key": key, "value": value}],
                },
            }
        )
        print(payload)

        # Make the initial POST request to send the templated message
        response = requests.post(url, headers=self.__headers, data=payload)
        response_json = response.json()
        # Log the message in the Messagge model, storing the response
        Messagge.objects.create(
            messages=value,  # Assuming this is your message content
            channel=self.__channel_instance,
            provider=self.__provider_instance,
            customer=customer_instance,
            result=response_json,  # Store the response from MessageBird
            retries=0,  # Initial retry count set to 0
        )

        return response_json

    def send_template_image_otp(self, customer_id, message, image):
        """
        Sends a templated message to a customer via the Messagebird API.

        Args:
            customer_id (int): The ID of the customer.
            key (str): The key in the template that will be replaced by the value.
            value (str): The value that will replace the key in the template.

        Returns:
            dict: JSON response from the Messagebird API after sending the message.
        """
        customer_instance = Customer.objects.get(id=customer_id)
        phone_number = self.get_customer_phone(customer_id)

        url = f"{self.__base_url}workspaces/{self.__workspace_id}/channels/{self.__channel_id}/messages"
        print(url)

        # Prepare the payload for the first message (template)
        payload = json.dumps(
            {
                "receiver": {
                    "contacts": [
                        {
                            "identifierKey": "phonenumber",
                            "identifierValue": phone_number,
                        }
                    ]
                },
                "template": {
                    "projectId": self.__project_id_image_otp,
                    "version": "latest",
                    "locale": "es",
                    "parameters": [
                        {"type": "string", "key": "message", "value": message},
                        {"type": "string", "key": "image", "value": image},
                    ],
                },
            }
        )
        print(payload)

        # Make the initial POST request to send the templated message
        response = requests.post(url, headers=self.__headers, data=payload)
        response_json = response.json()
        # Log the message in the Messagge model, storing the response
        Messagge.objects.create(
            messages=image,  # Assuming this is your message content
            channel=self.__channel_instance,
            provider=self.__provider_instance,
            customer=customer_instance,
            result=response_json,  # Store the response from MessageBird
            retries=0,  # Initial retry count set to 0
        )

        return response_json

    def get_contact(self, customer_id):
        """
        Fetches contact details of a customer from the Messagebird API.

        Args:
            customer_id (int): The ID of the customer to fetch details for.

        Returns:
            dict: JSON response containing the customer's contact details.
        """
        url = (
            f"{self.__base_url}workspaces/{self.__workspace_id}/contacts/{customer_id}"
        )
        print(url, self.__headers)

        payload = {}

        # Send a GET request to fetch contact details
        response = requests.request("GET", url, headers=self.__headers, data=payload)
        json_response = json.loads(response.text)

        return json_response
