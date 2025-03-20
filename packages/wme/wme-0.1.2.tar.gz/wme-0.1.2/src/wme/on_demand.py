from enum import Enum
from pydantic import AliasChoices, BaseModel, Field
from typing import List, Optional, Dict, Any, Self, Union
from datetime import datetime
import urllib.parse
import httpx

from wme.auth import TokenResponse

ARTICLE_URL_PREFIX = "https://api.enterprise.wikimedia.com/v2/articles/"
STRUCTURED_CONTENT_URL_PREFIX = (
    "https://api.enterprise.wikimedia.com/v2/structured-contents/"
)

DEV_ARTICLE_URL_PREFIX = "https://api-beta-dv.wikipediaenterprise.org/v2/articles/"
DEV_STRUCTURED_CONTENT_URL_PREFIX = (
    "https://api-beta-dv.wikipediaenterprise.org/v2/structured-contents/"
)


class Protection(BaseModel):
    type: str
    level: str
    expiry: str


class VersionScores(BaseModel):
    prediction: Optional[bool] = None


class Version(BaseModel):
    identifier: int | None = None
    comment: Optional[str] = None
    tags: Optional[List[str]] = None
    has_tag_needs_citation: Optional[bool] = None
    is_minor_edit: Optional[bool] = None
    is_flagged_stable: Optional[bool] = None
    scores: Optional[Dict[str, VersionScores]] = None
    editor: Optional[Dict[str, Union[str, int, bool, List[str]]]] = None
    size: Optional[Dict[str, Union[int, str]]] = None
    is_breaking_news: Optional[bool] = None
    noindex: Optional[bool] = None
    number_of_characters: Optional[int] = None
    maintenance_tags: Optional[Dict[str, int]] = None


class PreviousVersion(BaseModel):
    identifier: int | None = None
    number_of_characters: Optional[int] = None


class MainEntity(BaseModel):
    identifier: str
    url: str


class AdditionalEntities(BaseModel):
    identifier: str
    url: str
    aspects: List[str]


class Categories(BaseModel):
    name: str
    url: str


class Templates(BaseModel):
    name: str
    url: str


class Redirects(BaseModel):
    name: str
    url: str


class Namespace(BaseModel):
    identifier: int


class InLanguage(BaseModel):
    identifier: str


class Image(BaseModel):
    content_url: str
    width: Optional[int] = None
    height: Optional[int] = None


class Event(BaseModel):
    identifier: str
    type: str
    date_created: datetime | None = None
    date_published: Optional[datetime] = None
    partition: Optional[int] = None
    offset: Optional[int] = None


class Visibility(BaseModel):
    text: bool
    editor: bool
    comment: bool


class ArticleLinks(BaseModel):
    text: str | None = None
    url: str
    images: Optional[List[Any]] = None


class SectionType(str, Enum):
    section = "section"
    list_ = "list"
    list_item = "list_item"
    paragraph = "paragraph"


class ArticleSections(BaseModel):
    name: Optional[str] = None
    type: SectionType
    value: Optional[str] = None
    links: Optional[List[ArticleLinks]] = None
    has_parts: Optional[List["ArticleSections"]] = None  # Recursive structure

    def __iter__(self):
        yield self
        for part in self.has_parts or []:
            yield from part


class InfoboxPart(BaseModel):
    name: Optional[str] = None
    type: str
    value: Optional[str] = None
    values: Optional[List[str]] = None
    has_parts: Optional[List[Any]] = None  # Recursive structure
    images: Optional[List[Image]] = None
    links: Optional[List[ArticleLinks]] = None


class License(BaseModel):
    name: str
    identifier: str
    url: str


class ArticleBody(BaseModel):
    html: Optional[str] = None
    wikitext: Optional[str] = None


class EnterpriseAPIResponse(BaseModel):
    name: str | None = None
    identifier: int | None = None
    abstract: Optional[str] = None
    watchers_count: Optional[int] = None
    date_modified: datetime | None = None
    date_created: datetime | None = None
    date_previously_modified: Optional[datetime] = None
    protection: Optional[List[Protection]] = None
    version: Version | None = None
    previous_version: Optional[PreviousVersion] = None
    url: str | None = None
    namespace: Namespace | None = None
    in_language: InLanguage | None = None
    main_entity: Optional[MainEntity] = None
    additional_entities: Optional[List[AdditionalEntities]] = None
    categories: Optional[List[Categories]] = None
    templates: Optional[List[Templates]] = None
    redirects: Optional[List[Redirects]] = None
    is_part_of: Dict[str, str] | None = None
    article_body: ArticleBody | None = None
    license: List[License] | None = None
    visibility: Optional[Visibility] = None
    image: Optional[Image] = None
    event: Event | None = None
    description: Optional[str] = None

    # this field was renamed in the API, so we need to accept either infobox or infoboxes for backwards compatibility
    infobox: Optional[List[InfoboxPart]] = Field(
        default=None, validation_alias=AliasChoices("infobox", "infoboxes")
    )

    # this field was renamed in the API, so we need to accept either sections or article_sections for backwards compatibility
    article_sections: Optional[List[ArticleSections]] = Field(
        default=None, validation_alias=AliasChoices("sections", "article_sections")
    )

    def iter_sections(self):
        cur_section_name = None
        cur_section_value = ""
        for section in self.article_sections:
            for subsection in section:
                if subsection.type == SectionType.section:
                    if cur_section_name:
                        yield cur_section_name, cur_section_value
                    cur_section_name = subsection.name
                    cur_section_value = ""
                elif subsection.type == SectionType.paragraph:
                    if subsection.value:
                        cur_section_value += "\n" + subsection.value
                elif subsection.type == SectionType.list_:
                    for li in subsection.has_parts or []:
                        cur_section_value += "\n* " + li.value

        if cur_section_name:
            yield cur_section_name, cur_section_value


class Filter(BaseModel):
    field: str
    value: str

    @classmethod
    def for_site(cls, site: str = "enwiki") -> Self:
        return cls(field="is_part_of.identifier", value=site)


class OnDemand:
    def __init__(
        self, access_token: str | TokenResponse, client: httpx.AsyncClient | None = None
    ) -> None:
        if client is None:
            client = httpx.AsyncClient()
        if isinstance(access_token, TokenResponse):
            access_token = access_token.access_token
        self.access_token = access_token
        self.client = client

    async def _lookup(
        self,
        name: str,
        base_url: str,
        *,
        token: str,
        limit: int | None = None,
        fields: list[str] | None = None,
        filters: list[Filter] | None = None,
    ) -> list[EnterpriseAPIResponse]:
        name = urllib.parse.quote(name, safe="")
        url = base_url + name
        headers = {"Authorization": f"Bearer {token}"}
        query_params: dict[str, Any] = {}
        if limit:
            query_params["limit"] = limit
        if fields:
            query_params["fields"] = fields
        if filters:
            query_params["filters"] = [f.model_dump() for f in filters]
        response = await self.client.post(url, headers=headers, json=query_params)
        response.raise_for_status()
        return [EnterpriseAPIResponse(**article) for article in response.json()]

    async def lookup(
        self,
        name: str,
        *,
        limit: int | None = None,
        fields: list[str] | None = None,
        filters: list[Filter] | None = None,
    ) -> list[EnterpriseAPIResponse]:
        return await self._lookup(
            name,
            ARTICLE_URL_PREFIX,
            token=self.access_token,
            limit=limit,
            fields=fields,
            filters=filters,
        )

    async def lookup_structured(
        self,
        name: str,
        *,
        limit: int | None = None,
        fields: list[str] | None = None,
        filters: list | None = None,
    ) -> list[EnterpriseAPIResponse]:
        return await self._lookup(
            name,
            STRUCTURED_CONTENT_URL_PREFIX,
            token=self.access_token,
            limit=limit,
            fields=fields,
            filters=filters,
        )

    async def lookup_enwiki(
        self,
        name: str,
        *,
        fields: list[str] | None = None,
    ) -> EnterpriseAPIResponse | None:
        """
        Lookup an article on enwiki.
        Checks for redirects and returns the final article if it exists.
        """

        return await self._lookup_enwiki(name, ARTICLE_URL_PREFIX, fields=fields)

    async def lookup_enwiki_structured(
        self,
        name: str,
        *,
        fields: list[str] | None = None,
    ) -> EnterpriseAPIResponse | None:
        return await self._lookup_enwiki(
            name, STRUCTURED_CONTENT_URL_PREFIX, fields=fields
        )

    async def _lookup_enwiki(
        self,
        name: str,
        base_url: str,
        *,
        fields: list[str] | None = None,
        redirect_count: int = 5,
    ) -> EnterpriseAPIResponse | None:
        try:
            articles = await self._lookup(
                name,
                base_url,
                fields=fields,
                filters=[Filter.for_site("enwiki")],
                token=self.access_token,
                limit=1,
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                if redirect_count <= 0:
                    return None

                target = await self._check_enwiki_redirect(name)
                if target:
                    return await self._lookup_enwiki(
                        target,
                        fields=fields,
                        base_url=base_url,
                        redirect_count=redirect_count - 1,
                    )
                else:
                    return None
            raise
        return articles[0]

    async def _check_enwiki_redirect(self, title) -> str | None:
        """
        Check if the given title is a redirect on enwiki.
        Returns the target title if it is a redirect, or None if it is not.
        """

        URL = "https://en.wikipedia.org/w/api.php?action=query&redirects&format=json&formatversion=2&titles="
        title = urllib.parse.quote(title, safe="")
        response = await self.client.get(URL + title)
        response.raise_for_status()

        data = response.json()
        response = data.get("query", {})
        normalizations = response.get("normalized", [])

        redirects = response.get("redirects", [])

        if redirects:
            return redirects[0]["to"]

        if normalizations:
            return normalizations[0]["to"]

        return None
