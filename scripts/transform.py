#!/usr/bin/env python3
"""
transform.py — Convert asepbagja-content Hugo repo into a plain markdown blog.

Does four things:
  1. Build a slug-to-filepath map from all articles
  2. Parse frontmatter from every article
  3. Process each file: clean frontmatter, convert HTML to markdown, rewrite internal links
  4. Generate README.md at repo root listing all articles
"""

import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
EN_DIR = REPO_ROOT / "content" / "blog" / "en"
ID_DIR = REPO_ROOT / "content" / "blog" / "id"


# ---------------------------------------------------------------------------
# Step 1: Build slug → filepath map
# ---------------------------------------------------------------------------

def build_slug_map():
    slug_map = {}
    for directory in [EN_DIR, ID_DIR]:
        for md_file in sorted(directory.glob("*.md")):
            slug = md_file.stem
            slug_map[slug] = md_file
    return slug_map


# ---------------------------------------------------------------------------
# Frontmatter helpers
# ---------------------------------------------------------------------------

def parse_frontmatter(text):
    """Split text into (frontmatter_dict, body). frontmatter_dict values are raw strings."""
    if not text.startswith("---"):
        return {}, text

    end = text.find("\n---", 3)
    if end == -1:
        return {}, text

    fm_block = text[3:end].strip()
    body = text[end + 4:].lstrip("\n")

    # Simple YAML parser for the keys we care about
    fm = {}
    current_key = None
    current_list = None

    for line in fm_block.split("\n"):
        # List item
        if line.startswith("- ") and current_key is not None and current_list is not None:
            current_list.append(line[2:].strip())
        # Key: value
        elif ":" in line and not line.startswith(" "):
            # Flush any pending list
            if current_key and current_list is not None:
                fm[current_key] = current_list
                current_list = None
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            if value == "":
                # Likely a list follows
                current_key = key
                current_list = []
            else:
                current_key = key
                fm[key] = value
        # Continuation / sub-key — skip
        else:
            pass

    # Flush trailing list
    if current_key and current_list is not None:
        fm[current_key] = current_list

    return fm, body


def clean_value(v):
    """Strip surrounding quotes from a YAML string value."""
    if isinstance(v, str):
        v = v.strip()
        if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
            v = v[1:-1]
    return v


def build_clean_frontmatter(fm):
    """Reconstruct frontmatter keeping only title, date, categories, summary."""
    lines = ["---"]

    title = clean_value(fm.get("title", ""))
    if title:
        # Re-quote the title
        lines.append(f'title: "{title}"')

    date = clean_value(fm.get("date", ""))
    if date:
        # Normalize: keep only YYYY-MM-DD
        date_match = re.match(r"(\d{4}-\d{2}-\d{2})", date)
        if date_match:
            date = date_match.group(1)
        lines.append(f"date: {date}")

    categories = fm.get("categories", [])
    if categories:
        lines.append("categories:")
        for cat in categories:
            lines.append(f"- {clean_value(cat)}")

    summary = clean_value(fm.get("summary", ""))
    if summary:
        lines.append(f'summary: "{summary}"')

    lines.append("---")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Step 3: HTML → Markdown conversions
# ---------------------------------------------------------------------------

def convert_figure(body):
    """Convert <figure>...</figure> blocks to markdown images."""

    # With caption (multi-line, all on separate lines)
    pattern_with_caption = re.compile(
        r'<figure[^>]*>\s*'
        r'<img\s[^>]*?src=["\']([^"\']+)["\'][^>]*?alt=["\']([^"\']*)["\'][^>]*/>\s*'
        r'<figcaption[^>]*>(.*?)</figcaption>\s*'
        r'</figure>',
        re.DOTALL | re.IGNORECASE
    )
    # Also handle alt before src
    pattern_with_caption_alt_first = re.compile(
        r'<figure[^>]*>\s*'
        r'<img\s[^>]*?alt=["\']([^"\']*)["\'][^>]*?src=["\']([^"\']+)["\'][^>]*/>\s*'
        r'<figcaption[^>]*>(.*?)</figcaption>\s*'
        r'</figure>',
        re.DOTALL | re.IGNORECASE
    )

    def replace_with_caption(m):
        src = m.group(1).strip()
        alt = m.group(2).strip()
        caption = re.sub(r'<[^>]+>', '', m.group(3)).strip()
        return f"![{alt}]({src})\n*{caption}*"

    def replace_with_caption_alt_first(m):
        alt = m.group(1).strip()
        src = m.group(2).strip()
        caption = re.sub(r'<[^>]+>', '', m.group(3)).strip()
        return f"![{alt}]({src})\n*{caption}*"

    body = pattern_with_caption.sub(replace_with_caption, body)
    body = pattern_with_caption_alt_first.sub(replace_with_caption_alt_first, body)

    # Without caption — src then alt
    pattern_no_caption = re.compile(
        r'<figure[^>]*>\s*'
        r'<img\s[^>]*?src=["\']([^"\']+)["\'][^>]*?alt=["\']([^"\']*)["\'][^>]*/>\s*'
        r'</figure>',
        re.DOTALL | re.IGNORECASE
    )
    # Without caption — alt then src
    pattern_no_caption_alt_first = re.compile(
        r'<figure[^>]*>\s*'
        r'<img\s[^>]*?alt=["\']([^"\']*)["\'][^>]*?src=["\']([^"\']+)["\'][^>]*/>\s*'
        r'</figure>',
        re.DOTALL | re.IGNORECASE
    )

    body = pattern_no_caption.sub(lambda m: f"![{m.group(2).strip()}]({m.group(1).strip()})", body)
    body = pattern_no_caption_alt_first.sub(lambda m: f"![{m.group(1).strip()}]({m.group(2).strip()})", body)

    return body


def convert_youtube(body):
    """Convert YouTube iframe divs to thumbnail links."""
    pattern = re.compile(
        r'<div[^>]*class=["\'][^"\']*ratio[^"\']*["\'][^>]*>\s*'
        r'<iframe\s[^>]*?src=["\']https://www\.youtube\.com/embed/([^"\'?&]+)[^"\']*["\'][^>]*?title=["\']([^"\']*)["\'][^>]*?>\s*</iframe>\s*'
        r'</div>',
        re.DOTALL | re.IGNORECASE
    )

    def replace_youtube(m):
        vid_id = m.group(1).strip()
        title = m.group(2).strip()
        thumb = f"https://img.youtube.com/vi/{vid_id}/0.jpg"
        watch = f"https://www.youtube.com/watch?v={vid_id}"
        return f"[![{title}]({thumb})]({watch})"

    return pattern.sub(replace_youtube, body)


def convert_iframes(body):
    """Remove other iframes (e.g. Spotify embeds) — replace with empty line."""
    pattern = re.compile(r'<iframe[^>]*>.*?</iframe>', re.DOTALL | re.IGNORECASE)
    return pattern.sub('', body)


def convert_anchor_tags(body):
    """Convert <a href="URL">TEXT</a> to [TEXT](URL), skipping SVG attribution links."""
    # Unsplash SVG attribution links — remove entirely
    unsplash_pattern = re.compile(
        r'<a\s[^>]*href=["\'][^"\']*unsplash[^"\']*["\'][^>]*>.*?</a>',
        re.DOTALL | re.IGNORECASE
    )
    body = unsplash_pattern.sub('', body)

    # Any remaining <a href="...">...</a> with SVG inside — remove
    svg_link_pattern = re.compile(
        r'<a\s[^>]*>.*?<svg[^>]*>.*?</svg>.*?</a>',
        re.DOTALL | re.IGNORECASE
    )
    body = svg_link_pattern.sub('', body)

    # Plain text anchor tags
    anchor_pattern = re.compile(
        r'<a\s[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',
        re.DOTALL | re.IGNORECASE
    )

    def replace_anchor(m):
        href = m.group(1).strip()
        text = re.sub(r'<[^>]+>', '', m.group(2)).strip()
        if text:
            return f"[{text}]({href})"
        return href

    body = anchor_pattern.sub(replace_anchor, body)
    return body


def convert_italic_tags(body):
    """Convert <i>TEXT</i> to *TEXT*."""
    return re.sub(r'<i>(.*?)</i>', lambda m: f"*{m.group(1)}*", body, flags=re.DOTALL | re.IGNORECASE)


def remove_div_wrappers(body):
    """Remove <div ...> and </div> lines."""
    body = re.sub(r'<div[^>]*>', '', body)
    body = re.sub(r'</div>', '', body)
    return body


def remove_hr_tags(body):
    """Convert <hr .../> or <hr> to markdown --- separator."""
    body = re.sub(r'<hr[^>]*/>', '\n---\n', body)
    body = re.sub(r'<hr>', '\n---\n', body)
    return body


def collapse_blank_lines(body):
    """Replace 3+ consecutive blank lines with 2."""
    return re.sub(r'\n{3,}', '\n\n', body)


def process_html(body):
    """Apply all HTML → Markdown transformations."""
    body = convert_figure(body)
    body = convert_youtube(body)
    body = convert_iframes(body)
    body = convert_anchor_tags(body)
    body = convert_italic_tags(body)
    body = remove_hr_tags(body)
    body = remove_div_wrappers(body)
    body = collapse_blank_lines(body)
    return body


# ---------------------------------------------------------------------------
# Step 3c: Image URL rewriting
# ---------------------------------------------------------------------------

# Image directories that live under public/
_PUBLIC_DIRS = {"blog-img", "images", "music-img", "workspace-img", "portfolio-img"}


def rewrite_image_urls(body, article_path):
    """Rewrite image src URLs to relative paths pointing into public/.

    Handles two patterns:
      - https://www.asepbagja.com/blog-img/foo.jpg  (absolute with domain)
      - /blog-img/foo.jpg                            (Hugo root-relative)
    Both become e.g. ../../../public/blog-img/foo.jpg relative to article.
    """
    public_dir = REPO_ROOT / "public"

    def make_rel(img_path_str):
        """Given /blog-img/foo.jpg or a full URL, return relative path from article."""
        # Strip domain if present
        img_path_str = re.sub(r'https?://(?:www\.)?asepbagja\.com', '', img_path_str)
        # img_path_str is now like /blog-img/foo.jpg
        if not img_path_str.startswith('/'):
            return None
        parts = img_path_str.lstrip('/').split('/', 1)
        top_dir = parts[0]
        if top_dir not in _PUBLIC_DIRS:
            return None
        target = public_dir / img_path_str.lstrip('/')
        return os.path.relpath(target, article_path.parent)

    # Match ![alt](url) where url is asepbagja.com absolute or root-relative /dir/...
    pattern = re.compile(
        r'(!\[[^\]]*\])\(((?:https?://(?:www\.)?asepbagja\.com)?/(' +
        '|'.join(_PUBLIC_DIRS) +
        r')[^)]*)\)'
    )

    def replace_img(m):
        prefix = m.group(1)   # ![alt]
        url = m.group(2)
        rel = make_rel(url)
        if rel:
            return f"{prefix}({rel})"
        return m.group(0)

    return pattern.sub(replace_img, body)


# ---------------------------------------------------------------------------
# Step 3d: Internal link rewriting
# ---------------------------------------------------------------------------

def rewrite_internal_links(body, article_path, slug_map):
    """Replace asepbagja.com article links with relative .md paths."""

    # Match http/https, with or without www, but NOT image markdown (preceded by !)
    pattern = re.compile(r'(?<!!)\[([^\]]*)\]\((https?://(?:www\.)?asepbagja\.com[^)]*)\)')

    def replace_link(m):
        text = m.group(1)
        url = m.group(2)
        # Extract slug = last non-empty path segment
        path_part = re.sub(r'https?://(?:www\.)?asepbagja\.com', '', url).rstrip('/')
        slug = path_part.split('/')[-1] if path_part else ''

        if slug and slug in slug_map:
            target_path = slug_map[slug]
            # Compute relative path from article's directory to target
            rel = os.path.relpath(target_path, article_path.parent)
            return f"[{text}]({rel})"
        else:
            # Not found — leave as-is
            return m.group(0)

    return pattern.sub(replace_link, body)


# ---------------------------------------------------------------------------
# Step 3: Process all files
# ---------------------------------------------------------------------------

def process_file(md_file, slug_map):
    """Read, transform, and write back a markdown file. Returns metadata dict."""
    text = md_file.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)

    # Build clean frontmatter
    new_fm = build_clean_frontmatter(fm)

    # Process body HTML
    body = process_html(body)

    # Rewrite image URLs to local public/ paths
    body = rewrite_image_urls(body, md_file)

    # Rewrite internal links
    body = rewrite_internal_links(body, md_file, slug_map)

    # Write back
    new_text = new_fm + "\n\n" + body.lstrip("\n")
    md_file.write_text(new_text, encoding="utf-8")

    # Return metadata for README
    date_str = clean_value(fm.get("date", ""))
    date_match = re.match(r"(\d{4}-\d{2}-\d{2})", date_str) if date_str else None
    return {
        "title": clean_value(fm.get("title", md_file.stem)),
        "date": date_match.group(1) if date_match else "0000-00-00",
        "path": md_file,
    }


# ---------------------------------------------------------------------------
# Step 4: Generate README.md
# ---------------------------------------------------------------------------

def generate_readme(en_articles, id_articles):
    en_sorted = sorted(en_articles, key=lambda a: a["date"], reverse=True)
    id_sorted = sorted(id_articles, key=lambda a: a["date"], reverse=True)

    lines = [
        "# Asep Bagja's Blog",
        "",
        "Personal blog by [Asep Bagja Priandana](content/about/en.md) — programmer and musician living in Estonia.",
        "",
        "## English Articles",
        "",
    ]

    for art in en_sorted:
        rel_path = os.path.relpath(art["path"], REPO_ROOT)
        lines.append(f"- [{art['title']}]({rel_path}) — {art['date']}")

    lines += [
        "",
        "## Indonesian Articles",
        "",
    ]

    for art in id_sorted:
        rel_path = os.path.relpath(art["path"], REPO_ROOT)
        lines.append(f"- [{art['title']}]({rel_path}) — {art['date']}")

    lines.append("")

    readme = REPO_ROOT / "README.md"
    readme.write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated {readme}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Building slug map...")
    slug_map = build_slug_map()
    print(f"  Found {len(slug_map)} articles")

    en_articles = []
    id_articles = []

    for directory, articles_list in [(EN_DIR, en_articles), (ID_DIR, id_articles)]:
        lang = "en" if directory == EN_DIR else "id"
        files = sorted(directory.glob("*.md"))
        print(f"Processing {len(files)} {lang} articles...")
        for md_file in files:
            try:
                meta = process_file(md_file, slug_map)
                articles_list.append(meta)
                print(f"  OK  {md_file.name}")
            except Exception as e:
                print(f"  ERR {md_file.name}: {e}", file=sys.stderr)

    print("Generating README.md...")
    generate_readme(en_articles, id_articles)
    print("Done.")


if __name__ == "__main__":
    main()
