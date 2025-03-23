from typing import Optional, Any
from collections import defaultdict
from datetime import datetime

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
from marshmallow import fields

from .article import Visibility, PublicationStatus
from ._http_client import HttpClient


@dataclass_json
@dataclass(frozen=True)
class UpsertArticleParams:
    # author_id optionally identifies the user who last edited the article
    author_id: str

    # id is your identifier of choice for this article.
    id: str

    # title is the article's title. It may be empty if the article is a draft.
    title: str

    # description is an article's tagline. It may be empty.
    description: str

    # body is the main contents of an article. It may be empty if the article is a draft.
    body: str

    # visibility describes who can access this article, ranging from the
    # whole world (public) through to employees only (internal).
    visibility: Visibility

    # topic_id optionally identifies the topic that this
    # article is associated with. If given, you must have created
    # the topic first (see: UpsertArticleTopic)
    topic_id: str

    # status describes whether this article is published or not.
    status: PublicationStatus

    # created is when the topic was first created.
    created: datetime = field(
        metadata=config(
            encoder=datetime.isoformat,
            decoder=datetime.fromisoformat,
            mm_field=fields.DateTime(format="iso"),
        )
    )

    # last_edited is when the topic was last changed.
    last_edited: datetime = field(
        metadata=config(
            encoder=datetime.isoformat,
            decoder=datetime.fromisoformat,
            mm_field=fields.DateTime(format="iso"),
        )
    )

    # data optionally gives additional meta-data about the article.
    data: Optional[Any] = field(default_factory=lambda: defaultdict(dict))


def upsert_article(*, client: HttpClient, params: UpsertArticleParams) -> None:
    _ = client.post(
        path="articles",
        body=params.to_dict(),
    )
