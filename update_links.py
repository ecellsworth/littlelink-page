#!/usr/bin/env python3
"""
LittleLink Link Updater
Reads links.txt (in order) and rewrites the buttons inside index.html.
Edit links.txt → run this script → git commit & push.
"""

import re
from pathlib import Path

LINKS_FILE = Path("links.txt")
INDEX_FILE = Path("index.html")

# Known exceptions (brand → (css_suffix, icon_filename_without_svg, default_label))
OVERRIDES = {
    "youtube": ("yt", "youtube", "YouTube"),
    "yt": ("yt", "youtube", "YouTube"),
    "linkedin": ("linked", "linkedin", "LinkedIn"),
    "twitter": ("x", "x", "X"),
    "x": ("x", "x", "X"),
    "facebook": ("faceb", "facebook", "Facebook"),
    "tumblr": ("tumb", "tumblr", "Tumblr"),
    "buymeacoffee": ("coffee", "buymeacoffee", "Buy Me a Coffee"),
    "coffee": ("coffee", "buymeacoffee", "Buy Me a Coffee"),
    "email": ("default", "email", "Email"),
    "default": ("default", "littlelink", "Link"),
}

def load_links():
    links = []
    if not LINKS_FILE.exists():
        print("links.txt not found. Create it first.")
        return []
    for line in LINKS_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 2:
            continue
        brand = parts[0].lower()
        url = parts[1]
        label = parts[2] if len(parts) > 2 else None
        links.append((brand, url, label))
    return links

def make_button(brand, url, label):
    if brand in OVERRIDES:
        css, icon, default_label = OVERRIDES[brand]
    else:
        # Most brands use the same name for class and icon
        css = brand
        icon = brand
        default_label = brand.capitalize()

    if not label:
        label = default_label

    return f'''      <a class="button button-{css}" href="{url}" target="_blank" rel="noopener" role="button">
        <img class="icon" aria-hidden="true" src="images/icons/{icon}.svg" alt="{label} Logo">
        {label}
      </a>'''

def update_index(links):
    if not INDEX_FILE.exists():
        print("index.html not found.")
        return

    content = INDEX_FILE.read_text(encoding="utf-8")
    buttons = "\n".join(make_button(*item) for item in links)

    # Primary: replace everything inside the button-stack / nav
    pattern = r'(<(?:nav|div)[^>]*class="[^"]*button-stack[^"]*"[^>]*>)(.*?)(</(?:nav|div)>)'
    new_content, n = re.subn(
        pattern,
        lambda m: m.group(1) + "\n" + buttons + "\n    " + m.group(3),
        content,
        count=1,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # Fallback: use explicit markers if present
    if n == 0 and "<!-- LINKS-START -->" in content:
        pattern2 = r'(<!-- LINKS-START -->)(.*?)(<!-- LINKS-END -->)'
        new_content, n = re.subn(
            pattern2,
            r"\1\n" + buttons + r"\n    \3",
            content,
            count=1,
            flags=re.DOTALL,
        )

    if n == 0:
        print("Could not locate the button area.")
        print("Either keep the original button-stack or add markers:")
        print("  <!-- LINKS-START -->")
        print("  ...buttons...")
        print("  <!-- LINKS-END -->")
        return

    INDEX_FILE.write_text(new_content, encoding="utf-8")
    print(f"Updated index.html with {len(links)} link(s) in the order of links.txt")

if __name__ == "__main__":
    links = load_links()
    if links:
        update_index(links)
    else:
        print("No valid links found in links.txt")
