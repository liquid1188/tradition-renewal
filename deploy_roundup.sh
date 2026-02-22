#!/bin/bash
# ============================================================
# T&R Daily Roundup — One-Shot Deploy
# Paste this entire block into your DigitalOcean console
# ============================================================

echo "=================================="
echo "  T&R Daily Roundup — Deploying..."
echo "=================================="

# 1. Create project directory
mkdir -p /opt/t-and-r/roundups
cd /opt/t-and-r

# 2. Install dependencies
echo ""
echo "[1/4] Installing Python packages..."
pip3 install feedparser requests anthropic python-dateutil 2>/dev/null || pip3 install feedparser requests anthropic python-dateutil --break-system-packages

# 3. Write the roundup script
echo ""
echo "[2/4] Writing daily_roundup.py..."
cat > /opt/t-and-r/daily_roundup.py << 'PYEOF'
#!/usr/bin/env python3
"""
Tradition & Renewal — Daily Roundup Generator
Scans RSS feeds, classifies into 10 sections, generates briefing via Claude.
"""

import feedparser
import requests
import json
import os
import re
from datetime import datetime, timedelta
from time import mktime

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL = "claude-sonnet-4-5-20250929"

SECTIONS = {
    "Magisterial Monday": {
        "keywords": ["pope", "encyclical", "apostolic", "dicastery", "magisterium",
                     "vatican document", "papal teaching", "holy see", "doctrinal",
                     "congregation", "motu proprio", "apostolic exhortation"],
        "description": "Papal teaching, curial documents, doctrine"
    },
    "Liturgy": {
        "keywords": ["liturgy", "mass", "eucharist", "liturgical", "sacrament",
                     "sacred music", "gregorian chant", "rite", "missal", "worship",
                     "ordination", "communion", "altar", "vestment", "rubric"],
        "description": "Liturgical reform, rites, sacred music"
    },
    "AI & Catholic Anthropology": {
        "keywords": ["artificial intelligence", "AI", "transhumanism", "bioethics",
                     "human dignity", "technology ethics", "gene editing", "robot",
                     "algorithm", "surveillance", "digital", "imago dei", "cloning",
                     "euthanasia", "assisted suicide", "IVF"],
        "description": "Technology, bioethics, human dignity"
    },
    "Council & Crisis": {
        "keywords": ["vatican ii", "vatican council", "second vatican", "sacrosanctum",
                     "lumen gentium", "gaudium et spes", "dei verbum", "nostra aetate",
                     "conciliar", "post-conciliar", "aggiornamento", "ressourcement",
                     "traditionalist", "SSPX", "synod"],
        "description": "Vatican II documents, reception, reform"
    },
    "Papal Dispatch": {
        "keywords": ["vatican appointment", "cardinal", "bishop appointed",
                     "curial reform", "papal trip", "diplomatic", "nuncio",
                     "consistory", "resignation", "laicized", "vatican politics",
                     "holy see diplomacy", "concordat"],
        "description": "Vatican governance, appointments, diplomacy"
    },
    "The Legacy Shelf": {
        "keywords": ["book review", "new book", "catholic book", "theology book",
                     "publication", "publisher", "author", "memoir", "intellectual",
                     "patristic", "thomist", "scholarship"],
        "description": "Book reviews, intellectual tradition"
    },
    "Kydones Review": {
        "keywords": ["orthodox", "ecumenism", "eastern catholic", "patriarchate",
                     "constantinople", "moscow patriarchate", "filioque", "schism",
                     "catholic orthodox", "byzantine", "eastern church", "unity",
                     "tomos", "autocephaly"],
        "description": "Ecumenism, Orthodox-Catholic dialogue"
    },
    "Ad Gentes": {
        "keywords": ["interreligious", "interfaith", "islam", "muslim", "jewish",
                     "judaism", "protestant", "evangelical", "anglican", "buddhist",
                     "hindu", "dialogue", "missionary", "evangelization",
                     "nostra aetate", "religious freedom"],
        "description": "Interreligious dialogue"
    },
    "Nature & Grace": {
        "keywords": ["catholic culture", "film", "music", "art", "literature",
                     "pilgrimage", "personal faith", "testimony", "conversion",
                     "catholic life", "parish", "community"],
        "description": "Faith, culture, personal essays"
    },
    "Editor's Desk": {
        "keywords": ["breaking", "controversy", "scandal", "statement", "reaction",
                     "response", "debate", "opinion", "editorial", "crisis"],
        "description": "Short takes, editorial reactions"
    },
}

RSS_FEEDS = {
    "Vatican News": "https://www.vaticannews.va/en.rss.xml",
    "Catholic News Agency": "https://www.catholicnewsagency.com/feed",
    "National Catholic Reporter": "https://www.ncronline.org/rss.xml",
    "National Catholic Register": "https://www.ncregister.com/feed",
    "America Magazine": "https://www.americamagazine.org/feed",
    "The Pillar": "https://www.pillarcatholic.com/feed",
    "Catholic News Service": "https://www.catholicnews.com/feed/",
    "Crux": "https://cruxnow.com/feed",
    "Vatican Press Office": "https://press.vatican.va/content/salastampa/en.rss.xml",
    "Orthodox Times": "https://orthodoxtimes.com/feed/",
    "Ecumenical News": "https://www.ecumenicalnews.com/feed/",
    "Pray Tell Blog": "https://www.praytellblog.com/index.php/feed/",
    "New Liturgical Movement": "https://www.newliturgicalmovement.org/feeds/posts/default?alt=rss",
    "Church Life Journal": "https://churchlifejournal.nd.edu/feed/",
    "Where Peter Is": "https://wherepeteris.com/feed/",
    "AI Religion": "https://news.google.com/rss/search?q=artificial+intelligence+religion+ethics&hl=en-US",
    "Interfaith News": "https://news.google.com/rss/search?q=interreligious+dialogue+catholic&hl=en-US",
}


def fetch_feeds(hours_back=24):
    cutoff = datetime.now() - timedelta(hours=hours_back)
    articles = []
    for source, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:15]:
                pub_date = None
                for date_field in ['published_parsed', 'updated_parsed']:
                    if hasattr(entry, date_field) and getattr(entry, date_field):
                        pub_date = datetime.fromtimestamp(mktime(getattr(entry, date_field)))
                        break
                if pub_date and pub_date < cutoff:
                    continue
                summary = ""
                if hasattr(entry, 'summary'):
                    summary = re.sub(r'<[^>]+>', '', entry.summary)[:500]
                articles.append({
                    "source": source,
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "summary": summary,
                    "published": str(pub_date) if pub_date else "unknown",
                })
        except Exception as e:
            print(f"  Warning: {source}: {e}")
    print(f"  Fetched {len(articles)} articles from {len(RSS_FEEDS)} feeds")
    return articles


def classify_with_keywords(articles):
    for article in articles:
        text = f"{article['title']} {article['summary']}".lower()
        scores = {}
        for section, config in SECTIONS.items():
            score = sum(1 for kw in config["keywords"] if kw.lower() in text)
            if score > 0:
                scores[section] = score
        if scores:
            article["suggested_section"] = max(scores, key=scores.get)
        else:
            article["suggested_section"] = "Editor's Desk"
    return articles


def generate_roundup_with_claude(articles):
    if not ANTHROPIC_API_KEY:
        print("  No ANTHROPIC_API_KEY — using keyword-only mode")
        return generate_roundup_fallback(articles)

    article_text = ""
    for i, a in enumerate(articles[:80]):
        article_text += f"\n[{i+1}] SOURCE: {a['source']}\n"
        article_text += f"    TITLE: {a['title']}\n"
        article_text += f"    SUMMARY: {a['summary'][:200]}\n"
        article_text += f"    LINK: {a['link']}\n"
        article_text += f"    KEYWORD SUGGESTION: {a.get('suggested_section', 'unknown')}\n"

    sections_desc = "\n".join([f"- {name}: {cfg['description']}" for name, cfg in SECTIONS.items()])
    today = datetime.now().strftime('%B %d, %Y')

    prompt = f"""You are the editorial assistant for Tradition & Renewal, a Catholic Substack 
with 10 sections. Produce a daily news roundup.

SECTIONS:
{sections_desc}

TODAY'S ARTICLES:
{article_text}

INSTRUCTIONS:
1. Classify each article into the most appropriate section
2. Select the 3-5 most important stories per section (skip empty sections)
3. Write a 1-2 sentence summary for each in a scholarly but accessible tone
4. For each section with stories, write a 1-2 sentence editorial note
5. Flag stories deserving a full article response with a star

OUTPUT FORMAT:

# Daily Briefing — {today}

## [Section Name]
*Editorial note: ...*
- **[Headline]** — Summary. ([Source](link))

(Continue for each section with stories. Skip empty sections.)

---
### Stories to Watch
- Story 1: Why it matters
- Story 2: Why it matters

---
*Tradition & Renewal Daily Briefing — Compiled {today}*
"""

    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "Content-Type": "application/json",
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
            },
            json={
                "model": MODEL,
                "max_tokens": 4000,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=90,
        )
        data = response.json()
        if "content" in data:
            return data["content"][0]["text"]
        else:
            print(f"  API error: {data}")
            return generate_roundup_fallback(articles)
    except Exception as e:
        print(f"  Claude API error: {e}")
        return generate_roundup_fallback(articles)


def generate_roundup_fallback(articles):
    today = datetime.now().strftime("%B %d, %Y")
    output = f"# Daily Briefing — {today}\n\n"
    by_section = {}
    for a in articles:
        sec = a.get("suggested_section", "Editor's Desk")
        if sec not in by_section:
            by_section[sec] = []
        by_section[sec].append(a)
    for section_name in SECTIONS:
        stories = by_section.get(section_name, [])
        if not stories:
            continue
        output += f"## {section_name}\n"
        for story in stories[:5]:
            output += f"- **{story['title']}** — {story['summary'][:150]}... "
            output += f"([{story['source']}]({story['link']}))\n"
        output += "\n"
    output += f"\n---\n*Tradition & Renewal Daily Briefing — Compiled {today}*\n"
    return output


def save_roundup(content):
    today = datetime.now().strftime("%Y-%m-%d")
    os.makedirs("roundups", exist_ok=True)
    filepath = f"roundups/briefing_{today}.md"
    with open(filepath, "w") as f:
        f.write(content)
    with open("roundups/latest.md", "w") as f:
        f.write(content)
    print(f"  Saved to {filepath}")
    return filepath


if __name__ == "__main__":
    print("=" * 55)
    print("  TRADITION & RENEWAL — Daily Roundup Generator")
    print(f"  {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}")
    print("=" * 55)
    print()
    print("1. Fetching RSS feeds...")
    articles = fetch_feeds(hours_back=48)
    print(f"2. Classifying {len(articles)} articles...")
    articles = classify_with_keywords(articles)
    print("3. Generating roundup...")
    roundup = generate_roundup_with_claude(articles)
    print("4. Saving...")
    filepath = save_roundup(roundup)
    print()
    print("=" * 55)
    print("  Done! Check roundups/latest.md")
    print("=" * 55)
    print()
    print("PREVIEW (first 800 chars):")
    print("-" * 40)
    print(roundup[:800])
PYEOF

# 4. Set up cron job
echo ""
echo "[3/4] Setting up cron (6 AM EST = 11 UTC)..."
CRON_CMD="0 11 * * * cd /opt/t-and-r && /usr/bin/python3 daily_roundup.py >> /opt/t-and-r/roundups/cron.log 2>&1"
if crontab -l 2>/dev/null | grep -q "daily_roundup.py"; then
    echo "  Cron job already exists"
else
    (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
    echo "  Cron job added"
fi

# 5. Test run (keyword-only mode, no API key needed)
echo ""
echo "[4/4] Running test (keyword-only mode)..."
echo ""
cd /opt/t-and-r && python3 daily_roundup.py

echo ""
echo "=================================="
echo "  DEPLOYED!"
echo ""
echo "  To enable Claude-powered summaries:"
echo "  echo 'export ANTHROPIC_API_KEY=your_key' >> ~/.bashrc"
echo "  source ~/.bashrc"
echo ""
echo "  To view today's roundup:"
echo "  cat /opt/t-and-r/roundups/latest.md"
echo ""
echo "  Cron runs daily at 6 AM EST"
echo "=================================="
