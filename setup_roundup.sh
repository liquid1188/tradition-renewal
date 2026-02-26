#!/bin/bash
# ============================================================
# Tradition & Renewal — Daily Roundup Setup Script
# Run this on your DigitalOcean droplet (104.248.1.49)
# ============================================================

set -e

echo "=================================="
echo "  T&R Daily Roundup — Setup"
echo "=================================="

# 1. Create project directory
echo ""
echo "1. Creating project directory..."
sudo mkdir -p /opt/t-and-r/roundups
sudo chown -R $USER:$USER /opt/t-and-r

# 2. Install Python dependencies
echo ""
echo "2. Installing dependencies..."
pip3 install feedparser requests anthropic python-dateutil --break-system-packages

# 3. Copy the roundup script
echo ""
echo "3. Copying roundup script..."
cp daily_roundup.py /opt/t-and-r/daily_roundup.py
echo "  ✓ Copied to /opt/t-and-r/daily_roundup.py"

# 4. Environment variables — MUST be in /etc/environment, not .bashrc
# Cron runs in a minimal shell that never loads .bashrc. /etc/environment
# is sourced system-wide and is the correct place for cron-accessible vars.
echo ""
echo "4. Setting environment variables..."
echo ""
echo "  Run the following with your actual keys:"
echo ""
echo "  sudo tee -a /etc/environment << 'EOF'"
echo "  ANTHROPIC_API_KEY=your_anthropic_key_here"
echo "  RESEND_API_KEY=your_resend_key_here"
echo "  ROUNDUP_TO=alikoudis@likoudislegacy.com"
echo "  EOF"
echo ""
echo "  Then: source /etc/environment"
echo ""
echo "  *** /etc/environment is what cron reads — NOT .bashrc ***"

# 5. Cron job — 6 AM EST = 11:00 UTC
# The '. /etc/environment;' prefix loads the env vars into cron's shell.
echo ""
echo "5. Setting up cron job..."
CRON_CMD="0 11 * * * . /etc/environment; cd /opt/t-and-r && /usr/bin/python3 daily_roundup.py >> /opt/t-and-r/roundups/cron.log 2>&1"

if crontab -l 2>/dev/null | grep -q "daily_roundup.py"; then
    echo "  Replacing existing cron entry with updated version..."
    (crontab -l 2>/dev/null | grep -v "daily_roundup.py"; echo "$CRON_CMD") | crontab -
else
    (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
fi
echo "  ✓ Cron set: daily at 6 AM EST (11:00 UTC)"
echo "  ✓ Env vars sourced via: . /etc/environment"

echo ""
echo "=================================="
echo "  Done! To test immediately:"
echo "    cd /opt/t-and-r"
echo "    ANTHROPIC_API_KEY=xxx RESEND_API_KEY=xxx python3 daily_roundup.py"
echo ""
echo "  Watch cron output:"
echo "    tail -f /opt/t-and-r/roundups/cron.log"
echo "=================================="
