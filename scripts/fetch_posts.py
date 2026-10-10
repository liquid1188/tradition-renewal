#!/usr/bin/env python3
"""Pull every published post from the Tradition & Renewal Substack into posts.json.

Order of attempts:
1. Substack's archive API (full history).
2. The RSS feed (newest ~20 posts), merged into the existing posts.json so older posts are kept.
If Substack refuses both (it blocks GitHub's runner IPs with 403), keep posts.json as is,
emit a warning, and exit 0 so the workflow doesn't fail and email on every run.
If Substack blocks the runner, requests are retried through the r.jina.ai reader."""
import json, re, sys, urllib.request, urllib.error, html
import xml.etree.ElementTree as ET

PUB = "https://traditionandrenewal.substack.com"
OUT = "posts.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/129.0 Safari/537.36",
    "Accept": "application/json, application/rss+xml, text/xml, */*",
}

def fetch(url):
    """Try Substack directly; on a block (403/429), retry through the r.jina.ai reader,
    which fetches from its own servers and returns the raw response body."""
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        if e.code not in (403, 429):
            raise
        print(f"direct fetch got {e.code}, retrying via r.jina.ai")
    req = urllib.request.Request("https://r.jina.ai/" + url,
                                 headers={"X-Return-Format": "text"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()

def clean(t, n=200):
    t = html.unescape(re.sub(r"<[^>]+>", " ", t or ""))
    t = re.sub(r"\s+", " ", t).strip()
    return t[:n].rstrip() + ("…" if len(t) > n else "")

def from_archive():
    posts, seen, offset, limit = [], set(), 0, 50
    while True:
        batch = json.loads(fetch(f"{PUB}/api/v1/archive?sort=new&offset={offset}&limit={limit}"))
        if not batch:
            break
        for p in batch:
            if p.get("type") not in ("newsletter", "podcast", "thread", None):
                continue
            url = p.get("canonical_url") or f"{PUB}/p/{p.get('slug')}"
            if url in seen:
                continue
            seen.add(url)
            posts.append({
                "title": (p.get("title") or "").strip(),
                "excerpt": clean(p.get("subtitle") or p.get("description") or p.get("truncated_body_text")),
                "url": url,
                "date": (p.get("post_date") or "")[:10],
                "section": p.get("section_name") or "",
                "cover": p.get("cover_image") or "",
                "paid": p.get("audience") == "only_paid",
                "type": p.get("type") or "newsletter",
            })
        # Substack caps each page below the requested limit, so page until an empty batch
        offset += len(batch)
    return posts

def from_rss(old):
    from email.utils import parsedate_to_datetime
    root = ET.fromstring(fetch(f"{PUB}/feed"))
    known = {p["url"]: p for p in (old or [])}
    for it in root.iter("item"):
        url = (it.findtext("link") or "").strip()
        enc = it.find("enclosure")
        date = ""
        try:
            date = parsedate_to_datetime(it.findtext("pubDate")).strftime("%Y-%m-%d")
        except Exception:
            pass
        prev = known.get(url, {})
        known[url] = {
            "title": (it.findtext("title") or "").strip(),
            "excerpt": clean(it.findtext("description")) or prev.get("excerpt", ""),
            "url": url,
            "date": date or prev.get("date", ""),
            "section": prev.get("section", ""),
            "cover": (enc.get("url") if enc is not None else "") or prev.get("cover", ""),
            "paid": prev.get("paid", False),
            "type": prev.get("type", "newsletter"),
        }
    return list(known.values())

try:
    old = json.load(open(OUT))
except Exception:
    old = None

posts = None
for name, fn in (("archive API", from_archive), ("RSS feed", lambda: from_rss(old))):
    try:
        posts = fn()
        if posts:
            print(f"fetched {len(posts)} posts via {name}")
            break
    except Exception as e:
        print(f"{name} failed: {e}")

if not posts:
    print("::warning::Substack refused the request from this runner; posts.json left unchanged")
    sys.exit(0)

posts.sort(key=lambda x: x["date"], reverse=True)
if old == posts:
    print(f"posts.json unchanged ({len(posts)} posts)")
    sys.exit(0)
json.dump(posts, open(OUT, "w"), ensure_ascii=False, indent=1)
print(f"wrote {len(posts)} posts to {OUT}")
