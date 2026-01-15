#!/bin/bash

#
# Product Hunt Daily Emailer - Installation Script
# https://github.com/eyupucmaz/product-hunt-mailer
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Required Python version
REQUIRED_PYTHON="3.11"

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

# Print error
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Print info
print_info() {
    echo -e "${CYAN}ℹ $1${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Compare version numbers (returns 0 if $1 >= $2)
version_ge() {
    [ "$(printf '%s\n' "$2" "$1" | sort -V | head -n1)" = "$2" ]
}

# Get Python version
get_python_version() {
    if command_exists python3; then
        python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "0.0"
    else
        echo "0.0"
    fi
}

# Installation directory
INSTALL_DIR="$HOME/product-hunt-mailer"
UV_BIN="$HOME/.local/bin/uv"

print_banner

echo -e "This script will install Product Hunt Daily Emailer on your system."
echo -e "You will need:"
echo -e "  • Gemini API key (free): ${CYAN}https://aistudio.google.com/apikey${NC}"
echo -e "  • Resend API key (free): ${CYAN}https://resend.com${NC}"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

# Step 1: Install uv first (we need it to manage Python)
print_step "Checking uv installation..."
if command_exists uv; then
    print_success "uv is already installed"
elif [ -x "$UV_BIN" ]; then
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
    
    print_success "uv installed successfully"
fi

# Ensure uv is in PATH
export PATH="$HOME/.local/bin:$PATH"

# Step 2: Check/Install Python 3.11+
print_step "Checking Python $REQUIRED_PYTHON+ installation..."

CURRENT_PYTHON=$(get_python_version)

if version_ge "$CURRENT_PYTHON" "$REQUIRED_PYTHON"; then
    print_success "Python $CURRENT_PYTHON found (meets requirement)"
else
    print_warning "Python $CURRENT_PYTHON found, but $REQUIRED_PYTHON+ is required"
    print_info "Installing Python $REQUIRED_PYTHON using uv..."
    
    # Install Python using uv
    "$UV_BIN" python install $REQUIRED_PYTHON
    
    print_success "Python $REQUIRED_PYTHON installed via uv"
    print_info "uv will automatically use the correct Python version"
fi

# Step 3: Clone or update repository
print_step "Setting up project directory..."
if [ -d "$INSTALL_DIR" ]; then
    print_warning "Directory already exists: $INSTALL_DIR"
    read -p "Do you want to update it? (y/N): " UPDATE_REPO
    if [[ "$UPDATE_REPO" =~ ^[Yy]$ ]]; then
        cd "$INSTALL_DIR"
        git pull origin main
        print_success "Repository updated"
    fi
else
    git clone https://github.com/eyupucmaz/product-hunt-mailer.git "$INSTALL_DIR"
    print_success "Repository cloned to $INSTALL_DIR"
fi

cd "$INSTALL_DIR"

# Step 4: Install dependencies (uv will use the correct Python)
print_step "Installing dependencies..."
"$UV_BIN" sync
print_success "Dependencies installed"

# Step 5: Configure API keys
print_step "Configuring API keys..."
echo ""
echo -e "${YELLOW}Get your free API keys:${NC}"
echo -e "  Gemini: ${CYAN}https://aistudio.google.com/apikey${NC}"
echo -e "  Resend: ${CYAN}https://resend.com${NC}"
echo ""

read -p "Enter your Gemini API key: " GEMINI_KEY
read -p "Enter your Resend API key: " RESEND_KEY

cat > "$INSTALL_DIR/.env" << EOF
# Product Hunt Mailer - Environment Variables

GEMINI_API_KEY=$GEMINI_KEY
RESEND_API_KEY=$RESEND_KEY
EOF

print_success "API keys configured"

# Step 6: Configure email settings
print_step "Configuring email settings..."
echo ""

read -p "Enter sender email (e.g., digest@yourdomain.com): " SENDER_EMAIL
read -p "Enter sender name (e.g., Product Hunt Digest): " SENDER_NAME
read -p "Enter your name: " RECIPIENT_NAME
read -p "Enter your email address: " RECIPIENT_EMAIL

cat > "$INSTALL_DIR/config.yaml" << EOF
# Product Hunt Mailer Configuration

email:
  from: "$SENDER_NAME <$SENDER_EMAIL>"
  subject_prefix: "🚀 Product Hunt Daily"

recipients:
  - name: "$RECIPIENT_NAME"
    email: "$RECIPIENT_EMAIL"

settings:
  product_count: 5
  product_hunt_url: "https://www.producthunt.com"

gemini:
  model: "gemini-3-flash-preview"
EOF

print_success "Email settings configured"

# Step 7: Test the installation
print_step "Testing installation..."
echo ""
read -p "Do you want to send a test email now? (y/N): " SEND_TEST

if [[ "$SEND_TEST" =~ ^[Yy]$ ]]; then
    echo "Running test..."
    "$UV_BIN" run python -m src.main
fi

# Step 8: Setup cron job
print_step "Setting up scheduled execution..."
echo ""
echo "When do you want to receive the digest?"
echo "  1) Daily at 9:00 AM"
echo "  2) Daily at 8:00 AM and 6:00 PM"
echo "  3) Weekdays at 9:00 AM"
echo "  4) Skip (I'll set it up manually)"
echo ""
read -p "Choose an option (1-4): " CRON_OPTION

CRON_CMD="cd $INSTALL_DIR && $UV_BIN run python -m src.main >> $INSTALL_DIR/cron.log 2>&1"

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
    
    # Add new cron job with PATH
    CRON_ENTRY="$CRON_SCHEDULE PATH=\$HOME/.local/bin:\$PATH $CRON_CMD"
    (crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -
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
