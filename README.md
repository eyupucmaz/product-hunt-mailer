# 🚀 Product Hunt Daily Emailer

A Python CLI tool that fetches Product Hunt's daily top launches, generates AI-powered summaries using Gemini, and sends a beautifully formatted email digest via Resend.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

<img width="762" height="264" alt="image" src="https://github.com/user-attachments/assets/f9c3b1e3-7c7d-4e4f-ba91-43bc3551ce3d" />
<img width="996" height="731" alt="image" src="https://github.com/user-attachments/assets/911540a8-3e2c-45e8-9406-9a8ebda48928" />
<img width="1097" height="1163" alt="image" src="https://github.com/user-attachments/assets/784b5857-8a88-44b9-962a-3cfd4eea736f" />




## ✨ Features

- 🔍 Scrapes top products from Product Hunt homepage
- 🤖 AI-powered summaries using Gemini 3 Flash Preview (free tier)
- 📧 Beautiful HTML email templates
- ⚙️ YAML-based configuration
- 🍓 Raspberry Pi cron job ready

## ⚡ One-Line Install (Raspberry Pi / Linux)

```bash
curl -fsSL https://raw.githubusercontent.com/eyupucmaz/product-hunt-mailer/main/install.sh | bash
```

This interactive script will:
- Install `uv` package manager
- Clone the repository
- Configure your API keys and email settings
- Set up a cron job for scheduled emails

## 📋 Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager
- [Gemini API key](https://aistudio.google.com/apikey) (free)
- [Resend API key](https://resend.com) (free tier available)

## 🚀 Manual Setup

### 1. Clone the repository

```bash
git clone https://github.com/eyupucmaz/product-hunt-mailer.git
cd product-hunt-mailer
```

### 2. Install dependencies

```bash
# Install uv if you haven't
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv sync
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
GEMINI_API_KEY=your_gemini_api_key_here
RESEND_API_KEY=your_resend_api_key_here
```

### 4. Configure email settings

```bash
cp config.example.yaml config.yaml
```

Edit `config.yaml` to set your recipients and sender email:

```yaml
email:
  from: "Product Hunt Digest <digest@yourdomain.com>"
  subject_prefix: "🚀 Product Hunt Daily"

recipients:
  - name: "Your Name"
    email: "you@example.com"
```

> **Note:** The sender email domain must be verified in your Resend dashboard.

### 5. Run

```bash
uv run python -m src.main
```

## 🍓 Raspberry Pi Deployment

### Install uv on Raspberry Pi

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

### Clone and Setup

```bash
cd ~
git clone https://github.com/eyupucmaz/product-hunt-mailer.git
cd product-hunt-mailer

uv sync

cp .env.example .env
cp config.example.yaml config.yaml
# Edit both files with your settings
```

### Test

```bash
uv run python -m src.main
```

### Setup Cron Job

```bash
crontab -e
```

Add one of these lines:

```bash
# Daily at 9:00 AM
0 9 * * * cd /home/pi/product-hunt-mailer && /home/pi/.local/bin/uv run python -m src.main >> /home/pi/product-hunt-mailer/cron.log 2>&1

# Daily at 8:00 AM and 6:00 PM
0 8,18 * * * cd /home/pi/product-hunt-mailer && /home/pi/.local/bin/uv run python -m src.main >> /home/pi/product-hunt-mailer/cron.log 2>&1

# Weekdays only at 9:00 AM
0 9 * * 1-5 cd /home/pi/product-hunt-mailer && /home/pi/.local/bin/uv run python -m src.main >> /home/pi/product-hunt-mailer/cron.log 2>&1
```

> **Note:** Replace `/home/pi` with your actual home directory (`echo $HOME`)

## 📁 Project Structure

```
product-hunt-mailer/
├── .env.example          # Environment variables template
├── config.example.yaml   # Configuration template
├── pyproject.toml        # Dependencies
├── README.md
└── src/
    ├── __init__.py
    ├── main.py           # CLI entry point
    ├── scraper.py        # Product Hunt scraper
    ├── summarizer.py     # Gemini AI integration
    └── mailer.py         # Resend email sender
```

## ⚙️ Configuration Options

### `config.yaml`

| Option | Description |
|--------|-------------|
| `email.from` | Sender email (must be verified in Resend) |
| `email.subject_prefix` | Email subject prefix |
| `recipients` | List of recipients with name and email |
| `settings.product_count` | Number of products to include (1-10) |
| `gemini.model` | Gemini model to use |

### Gemini Models

| Model | Description |
|-------|-------------|
| `gemini-3-flash-preview` | Latest, fastest, recommended (free) |
| `gemini-2.5-flash` | Previous generation (free) |

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| `403 Forbidden` | The scraper uses browser impersonation to bypass bot detection. If issues persist, try updating `curl_cffi`. |
| `GEMINI_API_KEY required` | Make sure `.env` file exists and contains your API key (uncommented) |
| Cron not running | Use absolute paths for `uv` in crontab. Check with `which uv` |
| No email received | Check Resend dashboard for delivery status. Verify sender domain. |

## 📄 License

MIT License - feel free to use this for your own projects!

## 🙏 Credits

- [Product Hunt](https://www.producthunt.com) for the amazing product discovery platform
- [Google Gemini](https://ai.google.dev) for AI summarization
- [Resend](https://resend.com) for email delivery
