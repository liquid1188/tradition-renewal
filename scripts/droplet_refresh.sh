#!/bin/bash
# Refresh posts.json from Substack and push. Runs from cron on the droplet,
# since Substack returns 403 to GitHub Actions runners.
set -e
cd /opt/tradition-renewal
git pull -q --rebase
python3 scripts/fetch_posts.py
git add posts.json
git diff --cached --quiet || {
  git -c user.name="tradition-renewal-bot" -c user.email="actions@users.noreply.github.com" \
    commit -qm "Auto: refresh posts.json from Substack"
  git push -q
}
