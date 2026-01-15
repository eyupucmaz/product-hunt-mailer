"""Gemini AI summarizer module - Generates product summaries using Gemini API."""

import os
from dataclasses import dataclass

import google.generativeai as genai

from src.scraper import Product


# System instruction for the Gemini model
SYSTEM_INSTRUCTION = """You are a tech product analyst and newsletter writer for Product Hunt daily digests.

Your task is to create engaging, concise summaries of new product launches.

For each product, you will receive:
- Product name
- Tagline
- Topics/Categories

You must provide:
1. A brief 2-3 sentence summary explaining what the product does and its key value proposition
2. A "Why it matters" insight (1 sentence) about who would benefit from this product

Guidelines:
- Be concise and informative
- Use an engaging, professional tone suitable for a newsletter
- Avoid marketing fluff - focus on practical utility
- Highlight unique or innovative aspects when relevant
- Keep each product summary under 100 words total

Format your response as JSON with the following structure for each product:
{
    "products": [
        {
            "name": "Product Name",
            "summary": "Your 2-3 sentence summary here.",
            "why_it_matters": "Your insight about who benefits."
        }
    ],
    "intro": "A brief 1-2 sentence intro for today's digest."
}"""


@dataclass
class ProductSummary:
    """Summarized product information."""

    name: str
    original_tagline: str
    summary: str
    why_it_matters: str
    url: str
    image_url: str
    topics: list[str]
    comments_count: int


@dataclass
class DigestContent:
    """Complete digest content."""

    intro: str
    products: list[ProductSummary]


class GeminiSummarizer:
    """Summarizer using Gemini AI."""

    def __init__(self, api_key: str | None = None, model_name: str = "gemini-3-flash-preview"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required. Set it in .env or pass it directly.")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=SYSTEM_INSTRUCTION,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.7,
            ),
        )

    def summarize_products(self, products: list[Product]) -> DigestContent:
        """Generate summaries for a list of products."""
        if not products:
            return DigestContent(intro="No products found today.", products=[])

        # Build the prompt with product information
        product_info = "\n\n".join(
            f"Product {i + 1}:\n"
            f"- Name: {p.name}\n"
            f"- Tagline: {p.tagline}\n"
            f"- Topics: {', '.join(p.topics) if p.topics else 'N/A'}"
            for i, p in enumerate(products)
        )

        prompt = f"""Please summarize these {len(products)} Product Hunt launches for today's digest:

{product_info}

Remember to provide a JSON response with summaries for each product and a brief intro."""

        # Generate content
        response = self.model.generate_content(prompt)

        # Parse the JSON response
        import json

        try:
            result = json.loads(response.text)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return self._create_fallback_digest(products)

        # Build ProductSummary objects
        summaries: list[ProductSummary] = []
        for i, product in enumerate(products):
            summary_data = result.get("products", [])[i] if i < len(result.get("products", [])) else {}
            summaries.append(
                ProductSummary(
                    name=product.name,
                    original_tagline=product.tagline,
                    summary=summary_data.get("summary", product.tagline),
                    why_it_matters=summary_data.get("why_it_matters", ""),
                    url=product.url,
                    image_url=product.image_url,
                    topics=product.topics,
                    comments_count=product.comments_count,
                )
            )

        intro = result.get("intro", "Here are today's top Product Hunt launches!")

        return DigestContent(intro=intro, products=summaries)

    def _create_fallback_digest(self, products: list[Product]) -> DigestContent:
        """Create a fallback digest if AI summarization fails."""
        summaries = [
            ProductSummary(
                name=p.name,
                original_tagline=p.tagline,
                summary=p.tagline,
                why_it_matters="Check it out on Product Hunt!",
                url=p.url,
                image_url=p.image_url,
                topics=p.topics,
                comments_count=p.comments_count,
            )
            for p in products
        ]
        return DigestContent(
            intro="Here are today's top Product Hunt launches!",
            products=summaries,
        )


def summarize_products(
    products: list[Product],
    api_key: str | None = None,
    model_name: str = "gemini-3-flash-preview",
) -> DigestContent:
    """Convenience function to summarize products."""
    summarizer = GeminiSummarizer(api_key=api_key, model_name=model_name)
    return summarizer.summarize_products(products)
