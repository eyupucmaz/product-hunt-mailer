# Product Hunt Daily Emailer

A Python CLI tool that fetches Product Hunt's daily top launches, generates AI-powered summaries using Gemini, and sends a beautifully formatted email digest via Resend.

## Features

- Scrapes top 5 products from Product Hunt homepage
- AI-powered summaries using Gemini 3 Flash Preview
- Beautiful HTML email templates
- Configurable recipients and settings
- Raspberry Pi cron job ready

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- Gemini API key ([Get one free](https://aistudio.google.com/apikey))
- Resend API key ([Sign up](https://resend.com))

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd product-hunt-mailer

# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Configuration

Edit `config.yaml` to set:
- Email recipients
- Sender address
- Number of products to include

### Usage

```bash
# Run the emailer
uv run python -m src.main
```

## Raspberry Pi Deployment

### Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

### Setup Cron Job

```bash
crontab -e

# Add this line for daily 9 AM execution:
0 9 * * * cd /home/pi/product-hunt-mailer && /home/pi/.local/bin/uv run python -m src.main >> /home/pi/product-hunt-mailer/cron.log 2>&1
```

## License

MIT
