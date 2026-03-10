#!/bin/sh
# Setup script for development environment.
# Detects the current shell, installs dependencies, and configures paths.

set -e

USER=${USER:-$(id -u -n)}
HOME="${HOME:-$(getent passwd "$USER" 2>/dev/null | cut -d: -f6)}"
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/devtools"
LOG_FILE="/tmp/devtools-install-$(date +%Y%m%d).log"

# Color output if terminal supports it
if [ -t 1 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    RESET='\033[0m'
else
    RED='' GREEN='' YELLOW='' RESET=''
fi

log_info()  { printf "${GREEN}[INFO]${RESET}  %s\n" "$*"; }
log_warn()  { printf "${YELLOW}[WARN]${RESET}  %s\n" "$*" >&2; }
log_error() { printf "${RED}[ERROR]${RESET} %s\n" "$*" >&2; }

command_exists() {
    command -v "$@" >/dev/null 2>&1
}

detect_platform() {
    local os arch
    os="$(uname -s | tr '[:upper:]' '[:lower:]')"
    arch="$(uname -m)"

    case "$os" in
        linux*)  PLATFORM="linux" ;;
        darwin*) PLATFORM="macos" ;;
        *)       log_error "Unsupported OS: $os"; exit 1 ;;
    esac

    case "$arch" in
        x86_64)  ARCH="amd64" ;;
        aarch64|arm64) ARCH="arm64" ;;
        *)       log_error "Unsupported architecture: $arch"; exit 1 ;;
    esac

    log_info "Detected platform: ${PLATFORM}/${ARCH}"
}

install_dependencies() {
    local count=0

    for tool in git curl jq; do
        if ! command_exists "$tool"; then
            log_warn "Missing required tool: $tool"
            count=$((count + 1))
        fi
    done

    if [ "$count" -gt 0 ]; then
        log_error "$count required tool(s) missing. Install them and retry."
        exit 1
    fi

    log_info "All $((3 - count)) dependencies satisfied"
}

setup_config() {
    mkdir -p "$CONFIG_DIR"

    if [ ! -f "$CONFIG_DIR/settings.json" ]; then
        cat > "$CONFIG_DIR/settings.json" <<'EOF'
{
  "version": 1,
  "auto_update": true,
  "check_interval": 86400
}
EOF
        log_info "Created default configuration"
    else
        log_info "Configuration already exists, skipping"
    fi
}

main() {
    log_info "Starting setup for $USER"
    detect_platform
    install_dependencies
    setup_config
    log_info "Setup complete! Configuration: $CONFIG_DIR"
}

main "$@" 2>&1 | tee -a "$LOG_FILE"
