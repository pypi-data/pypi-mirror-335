import json
import logging
import os

import messagebird
import requests

logger = logging.getLogger(__name__)


class MessageBirdApi:
    __access_key = os.getenv("MB_ACCESS_KEY")
    __base_url = "https://api.bird.com/"
    __headers = {
        "Authorization": f"AccessKey {__access_key}",
        "Content-Type": "application/json",
    }

    def _init_(self, *args, **kwargs):
        try:
            print("Inicia el try")
            self.__access_key = os.getenv("MB_ACCESS_KEY")
            self.__base_url = "https://api.bird.com/"
            print(self.__access_key, "-----------------------", self.__base_url)
            self.__headers = {
                "Authorization": f"AccessKey {self.__access_key}",
                "Content-Type": "application/json",
            }
        except Exception as e:
            print(e)

    def get_contact(self, workspace_id, customer_id):
        url = f"{self.__base_url}workspaces/{workspace_id}/contacts/{customer_id}"
        print(url, self.__headers)
        payload = {}
        response = requests.request(
            "GET",
            url,
            headers=self.__headers,
            data=payload,
        )
        json_response = json.loads(response.text)
        return json_response

    def close_conversation(self, phone):
        try:
            # Inicializar el cliente de MessageBird con tu clave de API
            client = messagebird.Client(self.__access_key)

            # Número de teléfono del cliente
            customer_phone_number = f"+57{phone}"
            # Listar conversaciones
            conversations = client.conversation_list()

            # Buscar la conversación correspondiente al
            # número de teléfono del cliente
            conversation_id = None
            for conversation in conversations["items"]:
                if conversation["contact"]["msisdn"] == customer_phone_number:
                    conversation_id = conversation["id"]
                    break

            if conversation_id:
                # Cerrar la conversación
                client.conversation_update(
                    conversation_id,
                    {
                        "status": "archived",
                    },
                )

        except messagebird.client.ErrorException as e:
            for error in e.errors:
                logger.exception(error.description)
