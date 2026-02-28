#!/usr/bin/env python3
"""Export Disqus comments to per-article Markdown files.

Usage: python3 scripts/export_comments.py

Reads:  comments/asepnew-*-all.xml.gz
Writes: comments/<slug>.md  (one file per article slug with active comments)
"""

import gzip
import html
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import urlparse

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
COMMENTS_DIR = os.path.join(REPO_ROOT, "comments")
CONTENT_EN = os.path.join(REPO_ROOT, "content", "blog", "en")
CONTENT_ID = os.path.join(REPO_ROOT, "content", "blog", "id")

# Locate the gzipped XML (there should be exactly one)
xml_files = [
    f for f in os.listdir(COMMENTS_DIR) if f.endswith(".xml.gz")
]
if not xml_files:
    raise FileNotFoundError("No .xml.gz file found in comments/")
XML_PATH = os.path.join(COMMENTS_DIR, xml_files[0])

# Disqus XML namespaces
NS = {
    "d": "http://disqus.com",
    "dsq": "http://disqus.com/disqus-internals",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def dsq_id(element) -> str:
    """Return the dsq:id attribute of an element."""
    return element.get("{http://disqus.com/disqus-internals}id", "")


def text(element, tag: str, ns=NS) -> str:
    """Return stripped text of a child tag, or ''."""
    child = element.find(f"d:{tag}", ns)
    if child is None:
        return ""
    return (child.text or "").strip()


def html_to_md(raw: str) -> str:
    """Convert simple Disqus HTML comment body to Markdown."""
    t = html.unescape(raw)
    t = re.sub(r"<br\s*/?>", "\n", t)
    t = re.sub(r"<p>(.*?)</p>", r"\1\n\n", t, flags=re.DOTALL)
    t = re.sub(r"<strong>(.*?)</strong>", r"**\1**", t, flags=re.DOTALL)
    t = re.sub(r"<b>(.*?)</b>", r"**\1**", t, flags=re.DOTALL)
    t = re.sub(r"<em>(.*?)</em>", r"*\1*", t, flags=re.DOTALL)
    t = re.sub(r"<i>(.*?)</i>", r"*\1*", t, flags=re.DOTALL)
    t = re.sub(
        r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',
        r"[\2](\1)",
        t,
        flags=re.DOTALL,
    )
    t = re.sub(r"<[^>]+>", "", t)  # strip remaining tags
    # Collapse excessive blank lines
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def slug_from_link(link: str) -> str:
    """Extract the last non-empty path segment as slug."""
    path = urlparse(link).path.strip("/")
    return path.split("/")[-1] if path else ""


def format_date(iso: str) -> str:
    """Format ISO datetime string to YYYY-MM-DD."""
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00")).strftime("%Y-%m-%d")
    except ValueError:
        return iso[:10]


def find_article_path(slug: str) -> str:
    """Return relative path to the article .md file, or '(unknown)'."""
    en_path = os.path.join(CONTENT_EN, f"{slug}.md")
    id_path = os.path.join(CONTENT_ID, f"{slug}.md")
    if os.path.exists(en_path):
        return f"content/blog/en/{slug}.md"
    if os.path.exists(id_path):
        return f"content/blog/id/{slug}.md"
    return "(unknown)"


# ---------------------------------------------------------------------------
# Step 1 – Parse XML
# ---------------------------------------------------------------------------

print(f"Parsing {XML_PATH} …")
with gzip.open(XML_PATH, "rt", encoding="utf-8") as fh:
    root = ET.fromstring(fh.read())

# ---------------------------------------------------------------------------
# Step 2 – Extract threads
# ---------------------------------------------------------------------------

thread_map: dict[str, dict] = {}  # dsq_id → {link, title, isDeleted}

for thread in root.findall("d:thread", NS):
    tid = dsq_id(thread)
    if not tid:
        continue
    thread_map[tid] = {
        "link": text(thread, "link"),
        "title": text(thread, "title"),
        "isDeleted": text(thread, "isDeleted"),
    }

print(f"  Threads parsed: {len(thread_map)}")

# ---------------------------------------------------------------------------
# Step 3 – Extract active posts
# ---------------------------------------------------------------------------

post_map: dict[str, dict] = {}  # dsq_id → post dict (all active posts)

for post in root.findall("d:post", NS):
    if text(post, "isDeleted") != "false":
        continue
    if text(post, "isSpam") != "false":
        continue

    pid = dsq_id(post)
    if not pid:
        continue

    # message is in CDATA inside <message>
    msg_el = post.find("d:message", NS)
    message = (msg_el.text or "") if msg_el is not None else ""

    # author
    author_el = post.find("d:author", NS)
    author_name = ""
    if author_el is not None:
        author_name = text(author_el, "name")

    # thread reference
    thread_el = post.find("d:thread", NS)
    thread_id = dsq_id(thread_el) if thread_el is not None else ""

    # optional parent
    parent_el = post.find("d:parent", NS)
    parent_id = dsq_id(parent_el) if parent_el is not None else None

    post_map[pid] = {
        "message": message,
        "createdAt": text(post, "createdAt"),
        "author_name": author_name,
        "thread_id": thread_id,
        "parent_id": parent_id,
    }

print(f"  Active posts:   {len(post_map)}")

# ---------------------------------------------------------------------------
# Step 4 – Group threads by slug
# ---------------------------------------------------------------------------

slug_to_thread_ids: dict[str, list[str]] = {}
slug_to_title: dict[str, str] = {}

for tid, tdata in thread_map.items():
    if tdata["isDeleted"] == "true":
        continue
    slug = slug_from_link(tdata["link"])
    if not slug:
        continue
    slug_to_thread_ids.setdefault(slug, []).append(tid)
    # Keep the title (last one wins – they're usually identical)
    slug_to_title[slug] = tdata["title"]

# ---------------------------------------------------------------------------
# Step 5 – Group posts by slug and sort chronologically
# ---------------------------------------------------------------------------

slug_to_posts: dict[str, list[dict]] = {}

for pid, pdata in post_map.items():
    tid = pdata["thread_id"]
    # Find which slug this thread belongs to
    for slug, tids in slug_to_thread_ids.items():
        if tid in tids:
            entry = dict(pdata)
            entry["id"] = pid
            slug_to_posts.setdefault(slug, []).append(entry)
            break

# Sort each slug's posts by createdAt
for slug in slug_to_posts:
    slug_to_posts[slug].sort(key=lambda p: p["createdAt"])

# ---------------------------------------------------------------------------
# Step 9 – Write output files
# ---------------------------------------------------------------------------

os.makedirs(COMMENTS_DIR, exist_ok=True)

slugs_written = 0
for slug, posts in slug_to_posts.items():
    if not posts:
        continue

    title = slug_to_title.get(slug, slug)
    article_path = find_article_path(slug)
    total = len(posts)

    lines = [
        f"# Comments: {title}",
        "",
        f"**Article:** [{title}]({article_path})",
        f"**Total comments:** {total}",
        "",
        "---",
        "",
    ]

    for post in posts:
        author = post["author_name"] or "Anonymous"
        date_str = format_date(post["createdAt"])
        body = html_to_md(post["message"])

        # Build header line
        header = f"**{author}** · {date_str}"
        if post["parent_id"]:
            parent = post_map.get(post["parent_id"])
            if parent:
                parent_author = parent["author_name"] or "Anonymous"
                header += f" ↩ *reply to {parent_author}*"

        lines.append(header)
        lines.append("")
        lines.append(body)
        lines.append("")
        lines.append("---")
        lines.append("")

    out_path = os.path.join(COMMENTS_DIR, f"{slug}.md")
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))

    slugs_written += 1
    print(f"  Wrote {out_path}  ({total} comments)")

print(f"\nDone. {slugs_written} comment files written to comments/")
