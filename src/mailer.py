"""Email sender module - Sends digest emails via Resend API."""

import os
from dataclasses import dataclass
from datetime import datetime

import resend

from src.summarizer import DigestContent, ProductSummary


@dataclass
class Recipient:
    """Email recipient."""

    name: str
    email: str


def generate_html_email(digest: DigestContent) -> str:
    """Generate beautiful HTML email from digest content."""
    products_html = ""

    for i, product in enumerate(digest.products, 1):
        topics_html = " • ".join(
            f'<span style="color: #6b7280;">{topic}</span>' for topic in product.topics
        ) if product.topics else ""

        products_html += f"""
        <div style="margin-bottom: 32px; padding: 24px; background-color: #ffffff; border-radius: 12px; border: 1px solid #e5e7eb;">
            <div style="display: flex; align-items: flex-start; gap: 16px;">
                <img src="{product.image_url}" alt="{product.name}" style="width: 64px; height: 64px; border-radius: 12px; object-fit: cover;" />
                <div style="flex: 1;">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                        <span style="font-size: 12px; font-weight: 600; color: #da552f; background-color: #fff5f3; padding: 2px 8px; border-radius: 4px;">#{i}</span>
                        <a href="{product.url}" style="font-size: 18px; font-weight: 600; color: #1f2937; text-decoration: none;">{product.name}</a>
                    </div>
                    <p style="font-size: 14px; color: #6b7280; margin: 0 0 12px 0; font-style: italic;">"{product.original_tagline}"</p>
                    <p style="font-size: 15px; color: #374151; margin: 0 0 12px 0; line-height: 1.6;">{product.summary}</p>
                    {f'<p style="font-size: 14px; color: #059669; margin: 0 0 12px 0;"><strong>💡 Why it matters:</strong> {product.why_it_matters}</p>' if product.why_it_matters else ''}
                    <div style="display: flex; align-items: center; gap: 16px; font-size: 13px;">
                        <span style="color: #6b7280;">💬 {product.comments_count} comments</span>
                        {f'<span>{topics_html}</span>' if topics_html else ''}
                    </div>
                    <a href="{product.url}" style="display: inline-block; margin-top: 12px; padding: 8px 16px; background-color: #da552f; color: #ffffff; text-decoration: none; border-radius: 6px; font-size: 14px; font-weight: 500;">View on Product Hunt →</a>
                </div>
            </div>
        </div>
        """

    today = datetime.now().strftime("%B %d, %Y")

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Product Hunt Daily Digest</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f3f4f6; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
    <div style="max-width: 640px; margin: 0 auto; padding: 40px 20px;">
        <!-- Header -->
        <div style="text-align: center; margin-bottom: 32px;">
            <h1 style="font-size: 28px; font-weight: 700; color: #1f2937; margin: 0 0 8px 0;">🚀 Product Hunt Daily</h1>
            <p style="font-size: 14px; color: #6b7280; margin: 0;">{today}</p>
        </div>

        <!-- Intro -->
        <div style="background: linear-gradient(135deg, #da552f 0%, #f97316 100%); padding: 24px; border-radius: 12px; margin-bottom: 32px;">
            <p style="font-size: 16px; color: #ffffff; margin: 0; line-height: 1.6;">{digest.intro}</p>
        </div>

        <!-- Products -->
        <div style="margin-bottom: 32px;">
            <h2 style="font-size: 20px; font-weight: 600; color: #1f2937; margin: 0 0 20px 0;">Today's Top Launches</h2>
            {products_html}
        </div>

        <!-- Footer -->
        <div style="text-align: center; padding-top: 24px; border-top: 1px solid #e5e7eb;">
            <p style="font-size: 13px; color: #9ca3af; margin: 0 0 8px 0;">
                Powered by <a href="https://www.producthunt.com" style="color: #da552f; text-decoration: none;">Product Hunt</a> & <a href="https://ai.google.dev" style="color: #4285f4; text-decoration: none;">Gemini AI</a>
            </p>
            <p style="font-size: 12px; color: #9ca3af; margin: 0 0 12px 0;">
                You're receiving this because you subscribed to Product Hunt Daily Digest.
            </p>
            <p style="font-size: 12px; margin: 0;">
                <a href="https://github.com/eyupucmaz/product-hunt-mailer" style="color: #6b7280; text-decoration: none;">⭐ Star on GitHub</a>
            </p>
        </div>
    </div>
</body>
</html>"""

    return html


def generate_text_email(digest: DigestContent) -> str:
    """Generate plain text email from digest content."""
    today = datetime.now().strftime("%B %d, %Y")

    lines = [
        "🚀 PRODUCT HUNT DAILY DIGEST",
        f"   {today}",
        "",
        "=" * 50,
        "",
        digest.intro,
        "",
        "=" * 50,
        "",
        "TODAY'S TOP LAUNCHES",
        "",
    ]

    for i, product in enumerate(digest.products, 1):
        lines.extend([
            f"#{i} {product.name}",
            f"   \"{product.original_tagline}\"",
            "",
            f"   {product.summary}",
            "",
        ])
        if product.why_it_matters:
            lines.append(f"   💡 Why it matters: {product.why_it_matters}")
            lines.append("")
        lines.extend([
            f"   💬 {product.comments_count} comments",
            f"   🔗 {product.url}",
            "",
            "-" * 50,
            "",
        ])

    lines.extend([
        "Powered by Product Hunt & Gemini AI",
        "",
        "⭐ Star on GitHub: https://github.com/eyupucmaz/product-hunt-mailer",
        "",
    ])

    return "\n".join(lines)


class EmailSender:
    """Email sender using Resend API."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("RESEND_API_KEY")
        if not self.api_key:
            raise ValueError("RESEND_API_KEY is required. Set it in .env or pass it directly.")

        resend.api_key = self.api_key

    def send_digest(
        self,
        digest: DigestContent,
        recipients: list[Recipient],
        from_email: str,
        subject_prefix: str = "🚀 Product Hunt Daily",
    ) -> list[dict]:
        """Send digest to all recipients."""
        today = datetime.now().strftime("%Y-%m-%d")
        subject = f"{subject_prefix} - {today}"

        html_content = generate_html_email(digest)
        text_content = generate_text_email(digest)

        results = []

        for recipient in recipients:
            try:
                response = resend.Emails.send({
                    "from": from_email,
                    "to": [recipient.email],
                    "subject": subject,
                    "html": html_content,
                    "text": text_content,
                })
                results.append({
                    "recipient": recipient.email,
                    "status": "sent",
                    "id": response.get("id") if isinstance(response, dict) else getattr(response, "id", None),
                })
                print(f"✅ Email sent to {recipient.name} <{recipient.email}>")
            except Exception as e:
                results.append({
                    "recipient": recipient.email,
                    "status": "failed",
                    "error": str(e),
                })
                print(f"❌ Failed to send email to {recipient.name} <{recipient.email}>: {e}")

        return results


def send_digest(
    digest: DigestContent,
    recipients: list[Recipient],
    from_email: str,
    subject_prefix: str = "🚀 Product Hunt Daily",
    api_key: str | None = None,
) -> list[dict]:
    """Convenience function to send digest emails."""
    sender = EmailSender(api_key=api_key)
    return sender.send_digest(digest, recipients, from_email, subject_prefix)
