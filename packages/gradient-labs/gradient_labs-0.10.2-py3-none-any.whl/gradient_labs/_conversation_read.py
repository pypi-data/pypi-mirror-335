from ._http_client import HttpClient
from .conversation import Conversation


def read_conversation(*, client: HttpClient, conversation_id: str) -> Conversation:
    body = client.get(
        path=f"conversations/{conversation_id}",
        body={},
    )
    return Conversation.from_dict(body)
