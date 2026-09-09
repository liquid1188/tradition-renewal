#!/usr/bin/env python3
"""Pull every published post from the Tradition & Renewal Substack into posts.json.
Uses Substack's public archive API (the RSS feed only carries the newest few)."""
import json, re, sys, urllib.request, html

PUB = "https://traditionandrenewal.substack.com"
OUT = "posts.json"

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "tradition-renewal-site/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def excerpt(p):
    t = p.get("subtitle") or p.get("description") or p.get("truncated_body_text") or ""
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    t = re.sub(r"\s+", " ", t).strip()
    return t[:200].rstrip() + ("…" if len(t) > 200 else "")

posts, offset, limit = [], 0, 50
while True:
    batch = get(f"{PUB}/api/v1/archive?sort=new&offset={offset}&limit={limit}")
    if not batch:
        break
    for p in batch:
        if p.get("type") not in ("newsletter", "podcast", "thread", None):
            continue
        posts.append({
            "title": p.get("title", "").strip(),
            "excerpt": excerpt(p),
            "url": p.get("canonical_url") or f"{PUB}/p/{p.get('slug')}",
            "date": (p.get("post_date") or "")[:10],
            "section": p.get("section_name") or "",
            "cover": p.get("cover_image") or "",
            "paid": p.get("audience") == "only_paid",
            "type": p.get("type") or "newsletter",
        })
    if len(batch) < limit:
        break
    offset += limit

posts.sort(key=lambda x: x["date"], reverse=True)
try:
    old = json.load(open(OUT))
except Exception:
    old = None
if old == posts:
    print(f"posts.json unchanged ({len(posts)} posts)")
    sys.exit(0)
json.dump(posts, open(OUT, "w"), ensure_ascii=False, indent=1)
print(f"wrote {len(posts)} posts to {OUT}")
