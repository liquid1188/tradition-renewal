# Tradition & Renewal — Substack Implementation Guide (Final)

## Your 7 Sections

| # | Section | Color | Hex | Cadence |
|---|---------|-------|-----|---------|
| 1 | **Magisterial Monday** | Gold | #C3A364 | Every Monday (anchor) |
| 2 | **Liturgy** | Burgundy | #801824 | Rotating Wed/Fri |
| 3 | **AI & Catholic Anthropology** | Deep Teal | #1C4848 | Rotating Wednesday |
| 4 | **Council & Crisis** | Soft Navy | #263A5C | Rotating Wednesday |
| 5 | **Papal Dispatch** | Warm Bronze | #946C3E | Rotating Wednesday |
| 6 | **The Legacy Shelf** | Dark Burgundy | #581018 | Rotating Friday |
| 7 | **Kydones Review** | Muted Sage | #8E9B8C | Rotating Friday |
| 8 | **Nature & Grace** | Warm Sienna | #9C6634 | Rotating Friday |
| 9 | **Ad Gentes** | Deep Olive | #485834 | Rotating Wednesday |
| 10 | **Editor's Desk** | Slate | #525260 | As needed |

---

## Assets in This Package

### Images (18 total)

| File | Size | Purpose |
|------|------|---------|
| `banner_1140x378.png` | 1140×378 | Substack cover photo |
| `avatar_860x860.png` | 860×860 | Publication logo |
| `social_card_1200x675.png` | 1200×675 | Default social sharing image |
| `article_header_liturgy.png` | 1200×630 | Sample header: Liturgy |
| `article_header_ai_anthropology.png` | 1200×630 | Sample header: AI & Catholic Anthropology |
| `article_header_ecumenism.png` | 1200×630 | Sample header: Kydones Review |
| `article_header_council_crisis.png` | 1200×630 | Sample header: Council & Crisis |
| `article_header_magisterial_monday.png` | 1200×630 | Sample header: Magisterial Monday |
| `article_header_legacy_shelf.png` | 1200×630 | Sample header: The Legacy Shelf |
| `article_header_papal_dispatch.png` | 1200×630 | Sample header: Papal Dispatch |
| `series_liturgy.png` | 600×200 | Section badge |
| `series_ai_anthropology.png` | 600×200 | Section badge |
| `series_ecumenism.png` | 600×200 | Section badge |
| `series_council_crisis.png` | 600×200 | Section badge |
| `series_magisterial_monday.png` | 600×200 | Section badge |
| `series_legacy_shelf.png` | 600×200 | Section badge |
| `series_papal_dispatch.png` | 600×200 | Section badge |
| `brand_palette_reference.png` | 1200×1100 | Color/typography/section reference |

### Documents

| File | Purpose |
|------|---------|
| `ABOUT_PAGE.md` | Paste into Substack as a Page |
| `IMPLEMENTATION_GUIDE.md` | This file — your setup roadmap |
| `generate_branding_v2.py` | Python script for generating new headers |

---

## Step-by-Step Setup

### 1. Upload Publication Assets

Go to **Settings → Publication details**:
- **Logo:** Upload `avatar_860x860.png`
- **Cover photo:** Upload `banner_1140x378.png`
- **Social image:** Upload `social_card_1200x675.png`

### 2. Set Up Custom Domain

Purchase `traditionandrenewal.com` (~$12/year) and follow Substack's custom domain setup in Settings. This is the single biggest polish move.

### 3. Create Sections

Go to **Settings → Sections** and create all 7:

| Section Name | Slug |
|-------------|------|
| Magisterial Monday | `magisterial-monday` |
| Liturgy | `liturgy` |
| AI & Catholic Anthropology | `ai-catholic-anthropology` |
| Council & Crisis | `council-and-crisis` |
| Papal Dispatch | `papal-dispatch` |
| The Legacy Shelf | `the-legacy-shelf` |
| Kydones Review | `kydones-review` |
| Nature & Grace | `nature-and-grace` |
| Ad Gentes | `ad-gentes` |
| Editor's Desk | `editors-desk` |

Upload the corresponding `series_*.png` badge as the section image for each.

### 4. Create the About Page

Dashboard → Pages → New Page → paste `ABOUT_PAGE.md` → Publish as page.

### 5. Tag Existing Posts

Go through your back catalog and assign each post to the appropriate section.

---

## Weekly Publishing Rhythm (3 posts/week)

### Week A (sample)
| Day | Section | Example |
|-----|---------|---------|
| Mon | Magisterial Monday | "This Week: Leo XIV's address to the Synod on the Family" |
| Wed | Liturgy | "The Patristic Case for Standing at Communion" |
| Fri | The Legacy Shelf | "Reading Jungmann in 2026" |

### Week B (sample)
| Day | Section | Example |
|-----|---------|---------|
| Mon | Magisterial Monday | "This Week: New norms on seminary formation" |
| Wed | AI & Catholic Anthropology | "When the Machine Prays: AI and the Imago Dei" |
| Fri | Kydones Review | "The Filioque After Florence" |

### Week C (sample)
| Day | Section | Example |
|-----|---------|---------|
| Mon | Magisterial Monday | "This Week: Dicastery statement on liturgical translations" |
| Wed | Council & Crisis | "Sacrosanctum Concilium at Sixty" |
| Fri | Liturgy | "Why Sacred Music Still Matters" |

### Week D (sample)
| Day | Section | Example |
|-----|---------|---------|
| Mon | Magisterial Monday | "This Week: Leo meets Ecumenical Patriarch" |
| Wed | Papal Dispatch | "Leo Dissolves Children's Day Commission" |
| Fri | The Legacy Shelf | "A New Translation of Cornelius à Lapide" |

The key principle: Magisterial Monday is your **anchor** every week. Wednesday and Friday rotate through the other six sections. Over a month, every section gets at least one feature.

---

## Creating New Article Headers

Use the Python script to generate new headers for any article:

```python
from generate_branding_v2 import create_article_template, COLORS

# Section color map
SECTION_COLORS = {
    "Liturgy": (128, 24, 36),          # Burgundy
    "AI & Catholic Anthropology": (28, 72, 72),  # Deep Teal
    "Kydones Review": (142, 155, 140),            # Muted Sage
    "Nature & Grace": (156, 102, 52),              # Warm Sienna
    "Ad Gentes": (72, 88, 52),                     # Deep Olive
    "Editor's Desk": (82, 82, 96),                 # Slate
    "Council & Crisis": (38, 58, 92),            # Soft Navy
    "Magisterial Monday": (195, 163, 100),       # Gold
    "The Legacy Shelf": (88, 16, 24),            # Dark Burgundy
    "Papal Dispatch": (148, 108, 62),            # Warm Bronze
}

create_article_template(
    title="Your Article Title Here",
    category="Liturgy",
    filename="my_new_header.png",
    accent_color=SECTION_COLORS["Liturgy"]
)
```

---

## Distinguishing Magisterial Monday vs. Papal Dispatch

This is the most important editorial distinction in your section structure:

**Magisterial Monday** = What the Pope/magisterium **teaches**
- Encyclicals, apostolic exhortations, curial documents
- Doctrinal analysis, theological commentary
- "Here's what *Dilexit Nos* says about the Sacred Heart and why it matters"

**Papal Dispatch** = What the Pope/Vatican **does**
- Appointments, firings, curial restructuring
- Diplomatic meetings, political decisions
- "Leo just dissolved the Children's Day commission — here's the governance angle"

Think of it this way: Magisterial Monday is the *theology desk*. Papal Dispatch is the *Vatican bureau*.

---

## Brand Voice Quick Reference

| Do | Don't |
|----|-------|
| Ground arguments in primary sources | Rely on social media hot takes |
| Acknowledge complexity and nuance | Oversimplify into tribal camps |
| Critique ideas charitably | Attack persons |
| Use "the Church teaches" and cite documents | Use "I believe" without sourcing |
| Write for educated laity and clergy | Write only for academics |
| Treat Vatican II as authoritative | Dismiss or absolutize any single council |

---

*In Illo Uno Unum.*

---

## Daily Roundup Automation

Your `daily_roundup.py` script scans 18+ Catholic news RSS feeds every morning, classifies stories into your 10 sections using keyword matching + Claude API, and generates a formatted briefing.

### How It Works

1. **6 AM EST** — cron triggers `daily_roundup.py` on your DigitalOcean droplet
2. **RSS Scan** — fetches last 24 hours from Vatican News, CNA, NCR, The Pillar, America, Crux, Orthodox Times, New Liturgical Movement, and more
3. **Keyword Pre-Classification** — fast pass to bucket stories into sections
4. **Claude Refinement** — sends the pre-classified stories to Claude Sonnet for intelligent re-classification, summary writing, and editorial flagging
5. **Output** — saves `roundups/latest.md` with section-organized briefing + "Stories to Watch" flags

### Setup (on your droplet: 104.248.1.49)

```bash
# SSH in
ssh -i ~/.ssh/clawdbot_do root@104.248.1.49

# Run the setup script
bash setup_roundup.sh

# Set your API key
echo 'export ANTHROPIC_API_KEY=your_key' >> ~/.bashrc
source ~/.bashrc

# Test it
cd /opt/t-and-r
python3 daily_roundup.py
```

### RSS Sources (18 feeds)

| Category | Sources |
|----------|---------|
| Major Catholic News | Vatican News, CNA, NCR, NCRegister, America, The Pillar, CNS, Crux |
| Vatican/Institutional | Vatican Press Office |
| Ecumenical/Orthodox | Orthodox Times, Ecumenical News |
| Liturgy | Pray Tell Blog, New Liturgical Movement |
| Intellectual | Church Life Journal, Where Peter Is |
| AI/Tech Ethics | Google News (AI + religion + ethics) |
| Interreligious | Google News (interreligious + dialogue + catholic) |

### Using the Roundup

The daily briefing serves three purposes:

1. **Your reading list** — scan it over coffee, know what happened overnight
2. **Story ideas** — the ⭐ Stories to Watch flags are article prompts
3. **Magisterial Monday source** — Monday's briefing compiles into your weekly column

You can also paste the roundup directly into a Substack post as a "Daily Briefing" bonus for paid subscribers.

### Cost

At ~$0.02 per roundup (Claude Sonnet, ~4K output tokens), this costs roughly **$0.60/month** to run daily.

