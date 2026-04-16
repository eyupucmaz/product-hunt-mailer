#!/bin/bash

#
# Product Hunt Daily Emailer - Installation Script
# https://github.com/eyupucmaz/product-hunt-mailer
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Required Python version
REQUIRED_PYTHON="3.10"

# Installation directory
INSTALL_DIR="$HOME/product-hunt-mailer"
UV_BIN="$HOME/.local/bin/uv"
UV_CMD=""

# Print banner
print_banner() {
    echo -e "${CYAN}"
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║       🚀 Product Hunt Daily Emailer - Installer           ║"
    echo "║       https://github.com/eyupucmaz/product-hunt-mailer    ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Print step
print_step() {
    echo -e "\n${BLUE}▶ $1${NC}"
}

# Print success
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Print warning
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Print info
print_info() {
    echo -e "${CYAN}ℹ $1${NC}"
}

# Print error
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

escape_env() {
    local value="$1"
    value=${value//\\/\\\\}
    value=${value//\"/\\\"}
    value=${value//\$/\\$}
    printf '%s' "$value"
}

escape_yaml() {
    local value="$1"
    value=${value//\\/\\\\}
    value=${value//\"/\\\"}
    printf '%s' "$value"
}

prompt_required() {
    local prompt="$1"
    local var_name="$2"
    local value=""

    while true; do
        read -r -p "$prompt" value
        if [ -n "${value// /}" ]; then
            printf -v "$var_name" '%s' "$value"
            return
        fi
        print_error "This field is required."
    done
}

prompt_required_secret() {
    local prompt="$1"
    local var_name="$2"
    local value=""

    while true; do
        read -r -s -p "$prompt" value
        echo ""
        if [ -n "${value// /}" ]; then
            printf -v "$var_name" '%s' "$value"
            return
        fi
        print_error "This field is required."
    done
}

prompt_email() {
    local prompt="$1"
    local var_name="$2"
    local value=""

    while true; do
        read -r -p "$prompt" value
        if [[ "$value" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
            printf -v "$var_name" '%s' "$value"
            return
        fi
        print_error "Please enter a valid email address."
    done
}

prompt_yes_no() {
    local prompt="$1"
    local default="$2"
    local value=""

    while true; do
        read -r -p "$prompt" value
        if [ -z "$value" ]; then
            value="$default"
        fi
        case "$value" in
            [Yy]) return 0 ;;
            [Nn]) return 1 ;;
            *) print_error "Please enter y or n." ;;
        esac
    done
}

print_banner

echo -e "This script will install Product Hunt Daily Emailer on your system."
echo -e "You will need:"
echo -e "  • Gemini API key (free): ${CYAN}https://aistudio.google.com/apikey${NC}"
echo -e "  • Resend API key (free): ${CYAN}https://resend.com${NC}"
echo -e "  • Verified Resend domain: ${CYAN}https://resend.com/domains${NC}"
echo ""
read -r -p "Press Enter to continue or Ctrl+C to cancel..."

# Step 1: Check Python
print_step "Checking Python $REQUIRED_PYTHON+ installation..."
if command_exists python3; then
    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)
    MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
    MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)
    REQ_MAJOR=$(echo "$REQUIRED_PYTHON" | cut -d. -f1)
    REQ_MINOR=$(echo "$REQUIRED_PYTHON" | cut -d. -f2)

    if [ "$MAJOR" -gt "$REQ_MAJOR" ] || ([ "$MAJOR" -eq "$REQ_MAJOR" ] && [ "$MINOR" -ge "$REQ_MINOR" ]); then
        print_success "Python $PYTHON_VERSION found"
    else
        print_warning "Python $PYTHON_VERSION found, but $REQUIRED_PYTHON+ is required"
        print_info "uv will automatically download and manage Python $REQUIRED_PYTHON"
    fi
else
    print_warning "Python 3 is not installed"
    print_info "uv will automatically download and manage Python $REQUIRED_PYTHON"
fi

# Step 2: Install uv
print_step "Checking uv installation..."
if command_exists uv; then
    UV_CMD="$(command -v uv)"
    print_success "uv is already installed ($UV_CMD)"
elif [ -x "$UV_BIN" ]; then
    UV_CMD="$UV_BIN"
    print_success "uv found at $UV_BIN"
else
    print_warning "uv not found. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Add to PATH for this session
    export PATH="$HOME/.local/bin:$PATH"

    # Add to shell profile for future sessions
    SHELL_PROFILE=""
    if [ -f "$HOME/.bashrc" ]; then
        SHELL_PROFILE="$HOME/.bashrc"
    elif [ -f "$HOME/.zshrc" ]; then
        SHELL_PROFILE="$HOME/.zshrc"
    fi

    if [ -n "$SHELL_PROFILE" ]; then
        if ! grep -q '.local/bin' "$SHELL_PROFILE"; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_PROFILE"
        fi
    fi

    UV_CMD="$UV_BIN"
    print_success "uv installed successfully"
fi

# Ensure uv is in PATH
export PATH="$HOME/.local/bin:$PATH"

# Step 3: Clone or update repository
print_step "Setting up project directory..."
if [ -d "$INSTALL_DIR" ]; then
    print_warning "Directory already exists: $INSTALL_DIR"
    if prompt_yes_no "Do you want to update it? (y/N): " "N"; then
        cd "$INSTALL_DIR"
        git pull origin main
        print_success "Repository updated"
    fi
else
    git clone https://github.com/eyupucmaz/product-hunt-mailer.git "$INSTALL_DIR"
    print_success "Repository cloned to $INSTALL_DIR"
fi

cd "$INSTALL_DIR"

# Step 4: Install dependencies
print_step "Installing dependencies..."
"$UV_CMD" sync
print_success "Dependencies installed"

# Step 5: Configure .env and config.yaml
print_step "Collecting configuration values..."
echo ""
echo -e "${YELLOW}Get your free API keys:${NC}"
echo -e "  Gemini: ${CYAN}https://aistudio.google.com/apikey${NC}"
echo -e "  Resend: ${CYAN}https://resend.com${NC}"
echo ""

prompt_required_secret "Gemini API key: " GEMINI_KEY
prompt_required_secret "Resend API key: " RESEND_KEY
prompt_required "Verified Resend domain (e.g., yourdomain.com): " RESEND_DOMAIN
prompt_email "Sender email (e.g., digest@yourdomain.com): " SENDER_EMAIL
prompt_required "Sender name (e.g., Product Hunt Digest): " SENDER_NAME
prompt_required "Recipient name: " RECIPIENT_NAME
prompt_email "Recipient email: " RECIPIENT_EMAIL

SENDER_DOMAIN="${SENDER_EMAIL#*@}"
if [ "$SENDER_DOMAIN" != "$RESEND_DOMAIN" ]; then
    print_warning "Sender email domain ($SENDER_DOMAIN) does not match Resend domain ($RESEND_DOMAIN)."
    if ! prompt_yes_no "Continue anyway? (y/N): " "N"; then
        print_error "Installation aborted. Please rerun installer with matching domain values."
        exit 1
    fi
fi

echo ""
print_info "Configuration summary:"
echo -e "  Sender:    $SENDER_NAME <$SENDER_EMAIL>"
echo -e "  Recipient: $RECIPIENT_NAME <$RECIPIENT_EMAIL>"
echo -e "  Domain:    $RESEND_DOMAIN"
echo ""
if ! prompt_yes_no "Write .env and config.yaml with these values? (Y/n): " "Y"; then
    print_error "Installation aborted by user."
    exit 1
fi

GEMINI_KEY_ESCAPED="$(escape_env "$GEMINI_KEY")"
RESEND_KEY_ESCAPED="$(escape_env "$RESEND_KEY")"
RESEND_DOMAIN_ESCAPED="$(escape_env "$RESEND_DOMAIN")"
SENDER_EMAIL_ESCAPED="$(escape_yaml "$SENDER_EMAIL")"
SENDER_NAME_ESCAPED="$(escape_yaml "$SENDER_NAME")"
RECIPIENT_NAME_ESCAPED="$(escape_yaml "$RECIPIENT_NAME")"
RECIPIENT_EMAIL_ESCAPED="$(escape_yaml "$RECIPIENT_EMAIL")"

cat > "$INSTALL_DIR/.env" <<EOF_ENV
# Product Hunt Mailer - Environment Variables

GEMINI_API_KEY="$GEMINI_KEY_ESCAPED"
RESEND_API_KEY="$RESEND_KEY_ESCAPED"
RESEND_DOMAIN="$RESEND_DOMAIN_ESCAPED"
EOF_ENV

cat > "$INSTALL_DIR/config.yaml" <<EOF_CONFIG
# Product Hunt Mailer Configuration

email:
  from: "$SENDER_NAME_ESCAPED <$SENDER_EMAIL_ESCAPED>"
  subject_prefix: "🚀 Product Hunt Daily"

recipients:
  - name: "$RECIPIENT_NAME_ESCAPED"
    email: "$RECIPIENT_EMAIL_ESCAPED"

settings:
  product_count: 5
  product_hunt_url: "https://www.producthunt.com"

gemini:
  model: "gemini-3-flash-preview"
EOF_CONFIG

chmod 600 "$INSTALL_DIR/.env"
chmod 600 "$INSTALL_DIR/config.yaml"
print_success ".env and config.yaml configured"

# Step 6: Test the installation
print_step "Testing installation..."
echo ""
if prompt_yes_no "Do you want to send a test email now? (y/N): " "N"; then
    echo "Running test..."
    "$UV_CMD" run python -m src.main
fi

# Step 7: Setup cron job
print_step "Setting up scheduled execution..."
echo ""
echo "When do you want to receive the digest?"
echo "  1) Daily at 9:00 AM"
echo "  2) Daily at 8:00 AM and 6:00 PM"
echo "  3) Weekdays at 9:00 AM"
echo "  4) Skip (I'll set it up manually)"
echo ""
read -r -p "Choose an option (1-4): " CRON_OPTION

CRON_CMD="cd $INSTALL_DIR && PATH=\$HOME/.local/bin:\$PATH $UV_CMD run python -m src.main >> $INSTALL_DIR/cron.log 2>&1"

case $CRON_OPTION in
    1)
        CRON_SCHEDULE="0 9 * * *"
        ;;
    2)
        CRON_SCHEDULE="0 8,18 * * *"
        ;;
    3)
        CRON_SCHEDULE="0 9 * * 1-5"
        ;;
    *)
        CRON_SCHEDULE=""
        ;;
esac

if [ -n "$CRON_SCHEDULE" ]; then
    # Remove existing cron job if present
    crontab -l 2>/dev/null | grep -v "product-hunt-mailer" | crontab - 2>/dev/null || true

    # Add new cron job
    (crontab -l 2>/dev/null; echo "$CRON_SCHEDULE $CRON_CMD") | crontab -
    print_success "Cron job added: $CRON_SCHEDULE"
else
    print_warning "Skipped cron setup. You can run manually with:"
    echo "  cd $INSTALL_DIR && uv run python -m src.main"
fi

# Done!
echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              🎉 Installation Complete!                     ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Installation directory: ${CYAN}$INSTALL_DIR${NC}"
echo ""
echo -e "Useful commands:"
echo -e "  Run manually:    ${CYAN}cd $INSTALL_DIR && uv run python -m src.main${NC}"
echo -e "  View logs:       ${CYAN}tail -f $INSTALL_DIR/cron.log${NC}"
echo -e "  Edit config:     ${CYAN}nano $INSTALL_DIR/config.yaml${NC}"
echo -e "  Edit API keys:   ${CYAN}nano $INSTALL_DIR/.env${NC}"
echo -e "  View cron jobs:  ${CYAN}crontab -l${NC}"
echo ""
echo -e "⭐ Star on GitHub: ${CYAN}https://github.com/eyupucmaz/product-hunt-mailer${NC}"
echo ""
