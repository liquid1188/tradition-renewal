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
echo "3. Setting up roundup script..."
# (You'll SCP daily_roundup.py to /opt/t-and-r/)

# 4. Set up environment variable
echo ""
echo "4. Setting up API key..."
echo ""
echo "  Run this command with your actual Anthropic API key:"
echo "  echo 'export ANTHROPIC_API_KEY=your_key_here' >> ~/.bashrc"
echo "  source ~/.bashrc"

# 5. Set up cron job — runs at 6 AM EST every day
echo ""
echo "5. Setting up cron job..."
CRON_CMD="0 11 * * * cd /opt/t-and-r && /usr/bin/python3 daily_roundup.py >> /opt/t-and-r/roundups/cron.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "daily_roundup.py"; then
    echo "  Cron job already exists, skipping"
else
    (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
    echo "  ✓ Cron job added: daily at 6 AM EST (11 UTC)"
fi

# 6. Optional: email delivery setup
echo ""
echo "6. Email delivery (optional)..."
echo "  To get roundups emailed to you, install msmtp:"
echo "  sudo apt install msmtp msmtp-mta"
echo "  Then configure ~/.msmtprc with your SMTP settings"
echo ""
echo "  Add this line after save_roundup() in daily_roundup.py:"
echo '  os.system(f"cat {filepath} | mail -s \"T&R Daily Briefing\" andrew@likoudislegacy.com")'

echo ""
echo "=================================="
echo "  Setup complete!"
echo ""
echo "  Test it now:"
echo "    cd /opt/t-and-r"
echo "    python3 daily_roundup.py"
echo ""
echo "  The roundup will be saved to:"
echo "    /opt/t-and-r/roundups/latest.md"
echo ""
echo "  Cron runs daily at 6 AM EST"
echo "=================================="
