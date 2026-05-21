"""Main CLI entry point for Product Hunt Daily Emailer."""

from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

import yaml
from dotenv import load_dotenv

from src.mailer import Recipient, send_digest
from src.scraper import fetch_products
from src.summarizer import summarize_products


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(path) as f:
        return yaml.safe_load(f)


def main() -> int:
    """Main entry point."""
    print("=" * 60)
    print("🚀 Product Hunt Daily Emailer")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()

    # Load environment variables
    load_dotenv()

    # Load configuration
    try:
        config = load_config()
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return 1

    # Extract settings
    settings = config.get("settings", {})
    email_config = config.get("email", {})
    gemini_config = config.get("gemini", {})
    recipients_config = config.get("recipients", [])

    product_count = settings.get("product_count", 5)
    base_url = settings.get("product_hunt_url", "https://www.producthunt.com")
    proxy_url = (
        os.getenv("PROXY_URL")
        or os.getenv("HTTPS_PROXY")
        or os.getenv("HTTP_PROXY")
        or ""
    )
    proxy_url = proxy_url.strip() or None
    from_email = email_config.get("from", "Product Hunt Digest <digest@example.com>")
    subject_prefix = email_config.get("subject_prefix", "🚀 Product Hunt Daily")
    model_name = gemini_config.get("model", "gemini-3-flash-preview")

    # Parse recipients
    recipients = [
        Recipient(name=r.get("name", ""), email=r.get("email", ""))
        for r in recipients_config
        if r.get("email")
    ]

    if not recipients:
        print("❌ Error: No recipients configured in config.yaml")
        return 1

    print(f"📧 Recipients: {len(recipients)}")
    for r in recipients:
        print(f"   • {r.name} <{r.email}>")
    print()

    if proxy_url:
        print("🌐 Proxy enabled")
        print()

    # Step 1: Fetch products
    print(f"🔍 Fetching top {product_count} products from Product Hunt...")
    try:
        products = fetch_products(base_url=base_url, limit=product_count, proxy_url=proxy_url)
    except Exception as e:
        print(f"❌ Error fetching products: {e}")
        return 1

    if not products:
        print("⚠️  No products found. Exiting.")
        return 0

    print(f"✅ Found {len(products)} products:")
    for i, p in enumerate(products, 1):
        print(f"   {i}. {p.name} - {p.tagline[:50]}...")
    print()

    # Step 2: Generate summaries with Gemini
    print(f"🤖 Generating summaries with {model_name}...")
    try:
        digest = summarize_products(products, model_name=model_name)
    except Exception as e:
        print(f"❌ Error generating summaries: {e}")
        return 1

    print("✅ Summaries generated successfully!")
    print()

    # Step 3: Send emails
    print("📤 Sending digest emails...")
    try:
        results = send_digest(
            digest=digest,
            recipients=recipients,
            from_email=from_email,
            subject_prefix=subject_prefix,
        )
    except Exception as e:
        print(f"❌ Error sending emails: {e}")
        return 1

    # Summary
    print()
    print("=" * 60)
    successful = sum(1 for r in results if r.get("status") == "sent")
    failed = len(results) - successful
    print(f"📊 Summary: {successful} sent, {failed} failed")
    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
