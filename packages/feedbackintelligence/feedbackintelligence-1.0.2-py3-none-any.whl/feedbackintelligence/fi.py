import httpx
from typing import Optional, List, Dict

import requests

from feedbackintelligence.schemas import Context, Message


class FeedbackIntelligenceSDK:
    def __init__(self, api_key: str, base_url: str = "https://api.feedbackintelligence.ai"):
        """
        Initialize the SDK with the base URL of the API and an optional API key for authentication.

        :param api_key: Optional API key for authentication.
        """
        self.__base_url = base_url
        self.__headers = {
            'Content-Type': 'application/json',
        }
        if api_key:
            self.__headers['Authorization'] = f'Bearer {api_key}'

    def add_context(self, project_id: int, context: str, context_id: Optional[int] = None) -> Dict:
        """
        Add context to the database for later use in user messages (synchronous).

        :param  project_id: The ID of the project to which the context belongs.
        :param context: The context to add.
        :param context_id: Optional context ID.
        :return: Response from the API.
        """
        url = f"{self.__base_url}/data/{project_id}/context/add"
        payload = {"context": context}
        if context_id is not None:
            payload["id"] = context_id

        with httpx.Client() as client:
            response = client.post(url, json=payload, headers=self.__headers)
            response.raise_for_status()
            return response.json()

    async def add_context_async(self, project_id: int, context: str, context_id: Optional[int] = None) -> Dict:
        """
        Add context to the database for later use in user messages (asynchronous).

        :param  project_id: The ID of the project to which the context belongs.
        :param context: The context to add.
        :param context_id: Optional context ID.
        :return: Response from the API.
        """
        url = f"{self.__base_url}/data/{project_id}/context/add"
        payload = {"context": context}
        if context_id is not None:
            payload["id"] = context_id

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self.__headers)
            response.raise_for_status()
            return response.json()

    def add_chat(self, project_id: int, chat_id: str, messages: List[Message], user_id: Optional[str] = None,
                 version: Optional[str] = None) -> Dict:
        """
        Add chat data to the database (synchronous).

        :param  project_id: The ID of the project to which the chat data belongs.
        :param chat_id: The unique ID of the chat.
        :param messages: A list of messages in the chat.
        :param user_id: Optional ID of the user who initiated the chat.
        :param version: Optional version of the chat.
        :return: Response from the API.
        """
        url = f"{self.__base_url}/data/{project_id}/chat/add"
        payload = {
            "chat_id": chat_id,
            "messages": [message.to_dict() for message in messages],
        }
        if user_id is not None:
            payload["user_id"] = user_id
        if version:
            payload["version"] = version

        with httpx.Client() as client:
            response = client.post(url, json=payload, headers=self.__headers)
            response.raise_for_status()
            return response.json()

    async def add_chat_async(self, project_id: int, chat_id: str, messages: List[Message],
                             user_id: Optional[str] = None,
                             version: Optional[str] = "1.0") -> Dict:
        """
        Add chat data to the database (asynchronous).

        :param  project_id: The ID of the project to which the chat data belongs.
        :param chat_id: The unique ID of the chat.
        :param messages: A list of messages in the chat.
        :param user_id: Optional ID of the user who initiated the chat.
        :param version: Optional version of the chat.
        :return: Response from the API.
        """
        url = f"{self.__base_url}/data/{project_id}/chat/add"
        payload = {
            "chat_id": chat_id,
            "messages": [message.to_dict() for message in messages],
        }
        if user_id is not None:
            payload["user_id"] = user_id
        if version:
            payload["version"] = version

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self.__headers)
            response.raise_for_status()
            print('done!')
            return response.json()

    def add_feedback(self, project_id: int, source: str, message: str | None = None, user_id: Optional[str] = None,
                     thumbs_up: int | None = None, rating: float | None = None, message_id: str | None = None,
                     chat_id: Optional[str] = None, date: Optional[str] = None) -> Dict:
        """
        Add feedback data to the database (synchronous).

        :param  project_id: The ID of the project to which the feedback data belongs.
        :param source: The source of the feedback.
        :param message: The content of the feedback.
        :param user_id: Optional ID of the user who provided the feedback.
        :param thumbs_up: The thumbs up of the feedback 0 or 1 if exists.
        :param rating: The rating of the feedback if exists.
        :param message_id: The id of the message to add the feedback on.
        :param chat_id: Optional ID of the chat associated with the feedback.
        :param date: Optional date the feedback was given.
        :return: Response from the API.
        """
        url = f"{self.__base_url}/data/{project_id}/feedback/add"
        payload = {
            "source": source,
        }
        if message is not None:
            payload["message"] = message
        if user_id is not None:
            payload["user_id"] = user_id
        if chat_id is not None:
            payload["chat_id"] = chat_id
        if date:
            payload["date"] = date
        if thumbs_up is not None:
            payload["thumbs_up"] = thumbs_up
        if rating is not None:
            payload["rating"] = rating
        if message_id is not None:
            payload["message_id"] = message_id

        with httpx.Client() as client:
            response = client.post(url, json=payload, headers=self.__headers)
            response.raise_for_status()
            return response.json()

    async def add_feedback_async(self, project_id: int, message: str, source: str, user_id: Optional[str] = None,
                                 chat_id: Optional[str] = None, date: Optional[str] = None) -> Dict:
        """
        Add feedback data to the database (asynchronous).

        :param  project_id: The ID of the project to which the feedback data belongs.
        :param message: The content of the feedback.
        :param source: The source of the feedback.
        :param user_id: Optional ID of the user who provided the feedback.
        :param chat_id: Optional ID of the chat associated with the feedback.
        :param date: Optional date the feedback was given.
        :return: Response from the API.
        """
        url = f"{self.__base_url}/data/{project_id}/feedback/add"
        payload = {
            "message": message,
            "source": source,
        }
        if user_id is not None:
            payload["user_id"] = user_id
        if chat_id is not None:
            payload["chat_id"] = chat_id
        if date:
            payload["date"] = date

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self.__headers)
            response.raise_for_status()
            return response.json()


class BedrockWrapper:
    def __init__(self, bedrock_client, fi_api_key):
        """
                A wrapper for interacting with the Bedrock client and sending chat data to a custom endpoint via the FeedbackIntelligenceSDK.

                :param bedrock_client: An instance of the Bedrock client used to interact with Bedrock models.
                :param fi_api_key: The API key for authenticating with FeedbackIntelligenceSDK.
        """
        self.bedrock_client = bedrock_client
        self.__sdk = FeedbackIntelligenceSDK(fi_api_key)

    def __send_to_FI(self, context: str, prompt: str, query: str, answer: str, chat_id: str,
                     project_id: int):

        """
            Sends chat data to Feedback Intelligence.

            :param context: The context of the conversation or chat.
            :param prompt: The prompt that initiated the query.
            :param query: The human user's query or input.
            :param answer: The AI's response to the query.
            :param chat_id: The ID of the chat in which the query and answer are exchanged.
            :param project_id: The ID of the project to which the chat belongs.
            :return: None.
            :raises RequestException: If an error occurs while sending data to the custom endpoint.
        """
        try:
            messages = [
                Message(role='human', text=query, prompt=prompt,
                        context=Context(text=context)),
                Message(role='ai', text=answer)]
            for message in messages:
                print(message.to_dict())
            response = self.__sdk.add_chat(project_id=project_id, chat_id=chat_id, messages=messages)
        except requests.exceptions.RequestException as e:
            print(f"Error sending data to custom endpoint: {e}")

    def invoke_model(self, *, context: str, prompt: str, query: str, chat_id: str, project_id: int, get_resp: callable,
                     **kwargs, ):
        """
            Queries the Bedrock client for an AI-generated response and sends the chat data to a custom endpoint.

            :param context: The context of the conversation or chat.
            :param prompt: The prompt that initiated the query.
            :param query: The human user's query or input.
            :param chat_id: The ID of the chat in which the query and answer are exchanged.
            :param project_id: The ID of the project to which the chat belongs.
            :param get_resp: A callable that processes the Bedrock response to extract the AI-generated answer.
            :param kwargs: Additional keyword arguments to pass to the Bedrock client's `invoke_model` method.
            :return: The response from the Bedrock client.
        """

        response = self.bedrock_client.invoke_model(
            **kwargs
        )

        answer = get_resp(response)

        self.__send_to_FI(context=context, prompt=prompt, query=query, answer=answer, chat_id=chat_id,
                          project_id=project_id)

        return response
