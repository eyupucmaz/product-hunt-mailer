"""Product Hunt API client - Fetches top products via GraphQL."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

API_URL = "https://api.producthunt.com/v2/api/graphql"
GRAPHQL_QUERY = """query DailyTop($first: Int!, $after: DateTime!, $before: DateTime!) {
  posts(
    first: $first
    order: RANKING
    featured: true
    postedAfter: $after
    postedBefore: $before
  ) {
    edges {
      node {
        name
        tagline
                description
        url
        commentsCount
        thumbnail { url }
        topics { edges { node { name } } }
      }
    }
  }
}
"""


@dataclass
class Product:
    """Represents a Product Hunt product."""

    name: str
    tagline: str
    description: str
    url: str
    image_url: str
    topics: list[str]
    comments_count: int


def _format_datetime(value: datetime) -> str:
    return value.strftime("%Y-%m-%dT%H:%M:%SZ")


def _last_24h_range() -> tuple[str, str]:
    now = datetime.now(timezone.utc)
    after = now - timedelta(days=1)
    return _format_datetime(after), _format_datetime(now)


def _extract_topics(node: dict[str, Any]) -> list[str]:
    topics: list[str] = []
    for edge in node.get("topics", {}).get("edges", []) or []:
        name = (edge.get("node", {}) or {}).get("name")
        if name:
            topics.append(str(name).strip())
    return topics


def _format_errors(errors: list[dict[str, Any]]) -> str:
    messages: list[str] = []
    for error in errors:
        if not isinstance(error, dict):
            continue
        message = (
            error.get("message")
            or error.get("error_description")
            or error.get("error")
        )
        if message:
            messages.append(str(message))
    return "; ".join(messages) or "Unknown API error"


class ProductHuntClient:
    """Product Hunt GraphQL client."""

    def __init__(self, access_token: str, api_url: str = API_URL, timeout: int = 30):
        if not access_token or not access_token.strip():
            raise ValueError("PRODUCT_HUNT_TOKEN is required. Set it in .env or pass it directly.")
        self.access_token = access_token.strip()
        self.api_url = api_url
        self.timeout = timeout

    def fetch_top_products(self, limit: int = 5) -> list[Product]:
        after, before = _last_24h_range()
        payload = {
            "query": GRAPHQL_QUERY,
            "variables": {
                "first": int(limit),
                "after": after,
                "before": before,
            },
        }
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        response = httpx.post(
            self.api_url,
            json=payload,
            headers=headers,
            timeout=self.timeout,
        )
        response.raise_for_status()

        data = response.json()
        errors = data.get("errors") or []
        if errors:
            raise RuntimeError(_format_errors(errors))

        edges = data.get("data", {}).get("posts", {}).get("edges", []) or []
        products: list[Product] = []
        for edge in edges:
            node = edge.get("node") if isinstance(edge, dict) else None
            if not node:
                continue
            products.append(self._parse_product(node))

        return products

    def _parse_product(self, node: dict[str, Any]) -> Product:
        thumbnail = node.get("thumbnail") or {}
        return Product(
            name=str(node.get("name") or "").strip(),
            tagline=str(node.get("tagline") or "").strip(),
            description=str(node.get("description") or "").strip(),
            url=str(node.get("url") or "").strip(),
            image_url=str(thumbnail.get("url") or "").strip(),
            topics=_extract_topics(node),
            comments_count=int(node.get("commentsCount") or 0),
        )


def fetch_products(limit: int = 5, access_token: str | None = None) -> list[Product]:
    """Convenience function to fetch top products."""
    client = ProductHuntClient(access_token=access_token or "")
    return client.fetch_top_products(limit=limit)