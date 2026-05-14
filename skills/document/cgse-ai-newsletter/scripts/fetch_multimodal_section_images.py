#!/usr/bin/env python3
"""
Download two distinct, section-appropriate images for the newsletter multi-modal block.

Image 1 — mixed documents / desk / whiteboard (PPTX, PDF, inputs theme):
  Unsplash: Wonderlane — photo-1566699270403-3f7e3f340664
  https://unsplash.com/photos/office-table-with-pile-of-papers-6jA6eVsRJ6Q

Image 2 — monitor with bar chart (program schedule / timeline analytics theme):
  Unsplash: 1981 Digital — photo-1686061592689-312bbfb5c055
  https://unsplash.com/photos/a-computer-screen-with-a-bar-chart-on-it-yqaskj8lQBE

Usage:
  python fetch_multimodal_section_images.py --output-dir ~/Downloads
"""

import argparse
import os
import urllib.request

IMG1 = "https://images.unsplash.com/photo-1566699270403-3f7e3f340664?w=720&h=480&fit=crop&q=85&auto=format"
IMG2 = "https://images.unsplash.com/photo-1686061592689-312bbfb5c055?w=720&h=405&fit=crop&q=85&auto=format"


def download(url: str, path: str) -> int:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    return len(data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=os.path.expanduser("~/Downloads"))
    args = parser.parse_args()
    d = args.output_dir
    p1 = os.path.join(d, "newsletter_multimodal_mar26.jpg")
    p2 = os.path.join(d, "newsletter_multimodal2_mar26.jpg")
    n1 = download(IMG1, p1)
    n2 = download(IMG2, p2)
    print(f"Saved {p1} ({n1} bytes)")
    print(f"Saved {p2} ({n2} bytes)")


if __name__ == "__main__":
    main()
