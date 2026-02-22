#!/usr/bin/env python3
"""
Tradition & Renewal — Daily Roundup Generator
Scans RSS feeds and news sources, categorizes stories into your 10 sections,
and generates a formatted daily briefing ready to paste into Substack.

Run daily via cron on your DigitalOcean droplet (104.248.1.49):
  0 6 * * * cd /opt/t-and-r && python3 daily_roundup.py

Requirements:
  pip install feedparser requests anthropic python-dateutil

Environment variables:
  ANTHROPIC_API_KEY=your_key_here
"""

import feedparser
import requests
import json
import os
import re
from datetime import datetime, timedelta
from dateutil import parser as dateparser

# ============================================================
# CONFIGURATION
# ============================================================

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL = "claude-sonnet-4-5-20250929"

# Your 10 sections with keywords for classification
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
    "The Bookshelf": {
        "keywords": ["book review", "new book", "catholic book", "theology book",
                     "publication", "publisher", "author", "memoir", "intellectual",
                     "patristic", "thomist", "scholarship"],
        "description": "Book reviews, intellectual tradition"
    },
    "Ut Unum Sint": {
        "keywords": ["orthodox", "ecumenism", "eastern catholic", "patriarchate",
                     "constantinople", "moscow patriarchate", "filioque", "schism",
                     "catholic orthodox", "byzantine", "eastern church", "unity",
                     "tomos", "autocephaly"],
        "description": "Ecumenism, Orthodox-Catholic dialogue"
    },
    "Nature & Grace": {
        "keywords": ["catholic culture", "film", "music", "art", "literature",
                     "pilgrimage", "personal faith", "testimony", "conversion",
                     "catholic life", "parish", "community"],
        "description": "Faith, culture, personal essays"
    },
    "From the Foundation": {
        "description": "News from the Likoudis Legacy Foundation — conference announcements, writings of Dr. James Likoudis, Kydones Review journal updates, institutional developments.",
        "keywords": ["likoudis", "foundation", "conference", "orientale lumen", "kydones", "james likoudis", "ecumenism conference", "byzantine", "schism", "501c3", "nonprofit"]
    },
    "Editor's Desk": {
        "keywords": ["breaking", "controversy", "scandal", "statement", "reaction",
                     "response", "debate", "opinion", "editorial", "crisis"],
        "description": "Short takes, editorial reactions"
    },
}

# RSS feeds to scan — curated for Catholic news coverage
RSS_FEEDS = {
    # Major Catholic news
    "Vatican News": "https://www.vaticannews.va/en.rss.xml",
    "Catholic News Agency": "https://www.catholicnewsagency.com/feed",
    "National Catholic Reporter": "https://www.ncronline.org/rss.xml",
    "National Catholic Register": "https://www.ncregister.com/feed",
    "America Magazine": "https://www.americamagazine.org/feed",
    "The Pillar": "https://www.pillarcatholic.com/feed",
    "Catholic News Service": "https://www.catholicnews.com/feed/",
    "Crux": "https://cruxnow.com/feed",
    
    # Vatican / institutional
    "Vatican Press Office": "https://press.vatican.va/content/salastampa/en.rss.xml",
    
    # Ecumenical / Orthodox
    "Orthodox Times": "https://orthodoxtimes.com/feed/",
    "Ecumenical News": "https://www.ecumenicalnews.com/feed/",
    
    # Liturgy focused
    "Pray Tell Blog": "https://www.praytellblog.com/index.php/feed/",
    "New Liturgical Movement": "https://www.newliturgicalmovement.org/feeds/posts/default?alt=rss",
    
    # Intellectual / theological
    "Church Life Journal": "https://churchlifejournal.nd.edu/feed/",
    "Where Peter Is": "https://wherepeteris.com/feed/",
    
    # AI / tech ethics
    "AI Religion (Google News)": "https://news.google.com/rss/search?q=artificial+intelligence+religion+ethics&hl=en-US",
    
    # Interreligious
    "Interfaith News (Google News)": "https://news.google.com/rss/search?q=interreligious+dialogue+catholic&hl=en-US",
}


def fetch_feeds(hours_back=24):
    """Fetch all RSS feeds and return articles from the last N hours."""
    cutoff = datetime.now() - timedelta(hours=hours_back)
    articles = []
    
    for source, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:15]:  # Max 15 per feed
                # Parse publication date
                pub_date = None
                for date_field in ['published_parsed', 'updated_parsed']:
                    if hasattr(entry, date_field) and getattr(entry, date_field):
                        from time import mktime
                        pub_date = datetime.fromtimestamp(mktime(getattr(entry, date_field)))
                        break
                
                if pub_date and pub_date < cutoff:
                    continue
                
                # Extract clean text
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
            print(f"  ⚠ Error fetching {source}: {e}")
    
    print(f"  Fetched {len(articles)} articles from {len(RSS_FEEDS)} feeds")
    return articles


def classify_with_keywords(articles):
    """Quick keyword-based pre-classification."""
    for article in articles:
        text = f"{article['title']} {article['summary']}".lower()
        scores = {}
        for section, config in SECTIONS.items():
            score = sum(1 for kw in config["keywords"] if kw.lower() in text)
            if score > 0:
                scores[section] = score
        
        if scores:
            article["suggested_section"] = max(scores, key=scores.get)
            article["section_scores"] = scores
        else:
            article["suggested_section"] = "Editor's Desk"
            article["section_scores"] = {}
    
    return articles


def generate_roundup_with_claude(articles):
    """Send articles to Claude for intelligent categorization and summary."""
    
    if not ANTHROPIC_API_KEY:
        print("  ⚠ No ANTHROPIC_API_KEY set — using keyword classification only")
        return generate_roundup_from_keywords(articles)
    
    # Prepare article summaries for Claude
    article_text = ""
    for i, a in enumerate(articles[:80]):  # Cap at 80 to manage tokens
        article_text += f"\n[{i+1}] SOURCE: {a['source']}\n"
        article_text += f"    TITLE: {a['title']}\n"
        article_text += f"    SUMMARY: {a['summary'][:200]}\n"
        article_text += f"    LINK: {a['link']}\n"
        article_text += f"    KEYWORD SUGGESTION: {a.get('suggested_section', 'unknown')}\n"
    
    sections_desc = "\n".join([f"- {name}: {cfg['description']}" 
                               for name, cfg in SECTIONS.items()])
    
    prompt = f"""You are the editorial assistant for Tradition & Renewal, a Catholic Substack 
with 10 sections. Your job is to produce a daily news roundup.

SECTIONS:
{sections_desc}

TODAY'S ARTICLES:
{article_text}

INSTRUCTIONS:
1. Classify each article into the most appropriate section
2. Select the 3-5 most important stories per section (skip sections with nothing relevant)
3. Write a 1-2 sentence summary for each selected story in a scholarly but accessible tone
4. For each section that has stories, write a brief (1-2 sentence) editorial note connecting the stories
5. Flag any stories that deserve a full article response (mark as ⭐ STORY TO WATCH)

OUTPUT FORMAT (use this exact markdown structure):

# Daily Briefing — [Today's Date]

## Magisterial Monday
*Editorial note: ...*
- **[Headline]** — Summary. ([Source](link))

## Liturgy
...

(Continue for each section that has relevant stories. Skip empty sections.)

---
### ⭐ Stories to Watch
- Story 1: Why it matters for T&R
- Story 2: Why it matters for T&R

---
*Tradition & Renewal Daily Briefing — Compiled {datetime.now().strftime('%B %d, %Y')}*
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
            timeout=60,
        )
        data = response.json()
        return data["content"][0]["text"]
    except Exception as e:
        print(f"  ⚠ Claude API error: {e}")
        return generate_roundup_from_keywords(articles)


def generate_roundup_from_keywords(articles):
    """Fallback: generate roundup using keyword classification only."""
    today = datetime.now().strftime("%B %d, %Y")
    output = f"# Daily Briefing — {today}\n\n"
    
    # Group by section
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
    """Save the roundup to file and optionally email/post."""
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Save to file
    os.makedirs("roundups", exist_ok=True)
    filepath = f"roundups/briefing_{today}.md"
    with open(filepath, "w") as f:
        f.write(content)
    print(f"  ✓ Saved to {filepath}")
    
    # Save latest
    with open("roundups/latest.md", "w") as f:
        f.write(content)
    print(f"  ✓ Saved to roundups/latest.md")
    
    return filepath


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 55)
    print("  TRADITION & RENEWAL — Daily Roundup Generator")
    print(f"  {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}")
    print("=" * 55)
    print()
    
    print("1. Fetching RSS feeds...")
    articles = fetch_feeds(hours_back=24)
    
    print("2. Pre-classifying with keywords...")
    articles = classify_with_keywords(articles)
    
    print("3. Generating roundup with Claude...")
    roundup = generate_roundup_with_claude(articles)
    
    print("4. Saving...")
    filepath = save_roundup(roundup)
    
    print()
    print("=" * 55)
    print("  Done! Check roundups/latest.md")
    print("=" * 55)
    print()
    print("PREVIEW (first 500 chars):")
    print("-" * 40)
    print(roundup[:500])
