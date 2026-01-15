"""Product Hunt scraper module - Fetches and parses today's top products."""

from __future__ import annotations

import re
from dataclasses import dataclass

from bs4 import BeautifulSoup
from curl_cffi import requests


@dataclass
class Product:
    """Represents a Product Hunt product."""

    name: str
    tagline: str
    url: str
    image_url: str
    topics: list[str]
    comments_count: int


class ProductHuntScraper:
    """Scraper for Product Hunt homepage."""

    def __init__(self, base_url: str = "https://www.producthunt.com"):
        self.base_url = base_url

    def fetch_homepage(self) -> str:
        """Fetch the Product Hunt homepage HTML using browser impersonation."""
        # Use curl_cffi to impersonate Chrome 131 browser and bypass bot detection
        response = requests.get(
            self.base_url,
            impersonate="chrome131",
            timeout=30,
        )
        response.raise_for_status()
        return response.text

    def parse_products(self, html: str, limit: int = 5) -> list[Product]:
        """Parse products from the homepage HTML."""
        soup = BeautifulSoup(html, "html.parser")
        products: list[Product] = []

        # Find all product sections using data-test attribute pattern
        product_sections = soup.find_all(
            "section", attrs={"data-test": re.compile(r"^post-item-\d+$")}
        )

        for section in product_sections[:limit]:
            product = self._parse_product_section(section)
            if product:
                products.append(product)

        return products

    def _parse_product_section(self, section: BeautifulSoup) -> Product | None:
        """Parse a single product section."""
        try:
            # Extract product name
            name_span = section.find("span", attrs={"data-test": re.compile(r"^post-name-")})
            if not name_span:
                return None

            name_link = name_span.find("a")
            if not name_link:
                return None

            name = name_link.get_text(strip=True)
            product_path = name_link.get("href", "")
            url = f"{self.base_url}{product_path}" if product_path.startswith("/") else product_path

            # Extract tagline
            tagline_span = section.find("span", class_=lambda c: c and "text-secondary" in c)
            tagline = tagline_span.get_text(strip=True) if tagline_span else ""

            # Extract image URL
            img = section.find("img")
            image_url = ""
            if img:
                # Try to get from srcset first (higher quality), fallback to src
                srcset = img.get("srcset", "")
                if srcset:
                    # Get the first URL from srcset
                    first_src = srcset.split(",")[0].strip().split(" ")[0]
                    image_url = first_src
                else:
                    image_url = img.get("src", "")

            # Extract topics
            topics: list[str] = []
            topic_links = section.find_all("a", href=re.compile(r"^/topics/"))
            for link in topic_links:
                topic_text = link.get_text(strip=True)
                if topic_text:
                    topics.append(topic_text)

            # Extract comments count
            comments_count = 0
            # Find the comment button (first button with a number)
            buttons = section.find_all("button")
            for button in buttons:
                p_tag = button.find("p")
                if p_tag:
                    text = p_tag.get_text(strip=True)
                    if text.isdigit():
                        comments_count = int(text)
                        break

            return Product(
                name=name,
                tagline=tagline,
                url=url,
                image_url=image_url,
                topics=topics,
                comments_count=comments_count,
            )

        except Exception as e:
            print(f"Error parsing product section: {e}")
            return None

    def get_top_products(self, limit: int = 5) -> list[Product]:
        """Fetch and return the top products from Product Hunt."""
        html = self.fetch_homepage()
        return self.parse_products(html, limit=limit)


def fetch_products(base_url: str = "https://www.producthunt.com", limit: int = 5) -> list[Product]:
    """Convenience function to fetch top products."""
    scraper = ProductHuntScraper(base_url=base_url)
    return scraper.get_top_products(limit=limit)
