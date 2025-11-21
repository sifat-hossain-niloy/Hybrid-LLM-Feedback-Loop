#!/bin/bash
# Launch Chromium with remote debugging for automated submissions
#
# This script starts Chromium with:
# - Remote debugging on port 9222
# - User profile for persistent login
# - Necessary flags for automation

# Configuration
PROFILE="Sifat"
PORT=9222
USER_DATA_DIR="$HOME/Library/Application Support/Chromium-Profiles/${PROFILE}"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}   Chromium Launcher for Automated Solver${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo -e "${GREEN}Profile:${NC} ${PROFILE}"
echo -e "${GREEN}Port:${NC} ${PORT}"
echo -e "${GREEN}User Data:${NC} ${USER_DATA_DIR}"
echo ""

# Check if Chromium is already running on this port
if lsof -Pi :${PORT} -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Chromium is already running on port ${PORT}${NC}"
    echo ""
    echo "Options:"
    echo "  1. Close existing Chromium and restart"
    echo "  2. Continue with existing instance"
    echo ""
    read -p "Choice (1/2): " choice
    
    if [ "$choice" = "1" ]; then
        echo "Killing existing Chromium process..."
        PID=$(lsof -Pi :${PORT} -sTCP:LISTEN -t)
        kill $PID 2>/dev/null
        sleep 2
    else
        echo -e "${GREEN}✓${NC} Using existing Chromium instance"
        exit 0
    fi
fi

# Create profile directory if it doesn't exist
mkdir -p "$USER_DATA_DIR"

# Find Chromium executable
if [ -f "/Applications/Chromium.app/Contents/MacOS/Chromium" ]; then
    CHROMIUM="/Applications/Chromium.app/Contents/MacOS/Chromium"
elif [ -f "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]; then
    CHROMIUM="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    echo -e "${YELLOW}⚠️  Using Google Chrome instead of Chromium${NC}"
else
    echo -e "${YELLOW}❌ Chromium not found!${NC}"
    echo ""
    echo "Please install Chromium:"
    echo "  brew install --cask chromium"
    echo ""
    echo "Or use Google Chrome (already installed)"
    exit 1
fi

echo ""
echo -e "${GREEN}🚀 Launching Chromium...${NC}"
echo ""

# Launch Chromium with remote debugging
"$CHROMIUM" \
    --remote-debugging-port=${PORT} \
    --user-data-dir="$USER_DATA_DIR" \
    --no-first-run \
    --no-default-browser-check \
    "https://codeforces.com" \
    > /dev/null 2>&1 &

# Wait a moment for Chromium to start
sleep 3

# Check if it started successfully
if lsof -Pi :${PORT} -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Chromium is running on port ${PORT}${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "  1. Login to Codeforces if needed"
    echo "  2. Run the automated solver:"
    echo "     ${GREEN}venv/bin/python3 run_solver_2041A.py${NC}"
    echo ""
    echo -e "${YELLOW}Note:${NC} Keep this Chromium window open while solving problems"
    echo ""
else
    echo -e "${YELLOW}❌ Failed to start Chromium${NC}"
    echo "Please check the error messages above"
    exit 1
fi

