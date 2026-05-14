#!/usr/bin/env python3
"""
Capture AI Tool Adoption metrics screenshots from the dashboard.
Dynamically detects section boundaries to handle layout changes.

Usage:
    python3 capture_metrics.py [--output-dir ~/Downloads]
"""

import argparse
import os
from playwright.sync_api import sync_playwright

DASHBOARD_URL = "http://10.67.211.78:5000/"

def capture(output_dir):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 3000})
        page.goto(DASHBOARD_URL, timeout=15000)
        page.wait_for_load_state('networkidle', timeout=10000)

        # Collect ALL heading positions as a list (not dict) since
        # duplicate texts like "MICROSOFT COPILOT..." appear per section
        headings = page.query_selector_all('h2, h3, .section-header')
        all_headings = []
        for h in headings:
            box = h.bounding_box()
            if box:
                text = h.inner_text().strip().upper()
                all_headings.append((text, box['y']))

        # Find "Total (All Functions)" y-position
        total_matches = [y for t, y in all_headings if 'TOTAL' in t]
        total_y = total_matches[0] if total_matches else 296

        # Find the FIRST Copilot heading after total_y
        copilot_matches = sorted([y for t, y in all_headings
                                  if 'COPILOT' in t and y > total_y])
        copilot_y = copilot_matches[0] if copilot_matches else 730

        # Find next team section heading after copilot_y
        # Team headings are short names like "Debug", "FW Dev", not metric labels
        team_matches = sorted([y for t, y in all_headings
                               if y > copilot_y + 50
                               and 'COPILOT' not in t
                               and 'ADOPTION' not in t
                               and 'RATE' not in t
                               and 'SECTIONS' not in t])
        next_section_y = team_matches[0] if team_matches else copilot_y + 400

        # Image 1: Adoption Rate & Active Rate (AI Code + NABU trend charts)
        overview_path = os.path.join(output_dir, 'newsletter_img1_overview.png')
        page.screenshot(path=overview_path, full_page=True,
                        clip={'x': 15, 'y': max(0, total_y - 10), 'width': 1250,
                              'height': copilot_y - total_y + 10})

        # Image 2: Microsoft Copilot - Rates & Actions
        details_path = os.path.join(output_dir, 'newsletter_img2_copilot.png')
        page.screenshot(path=details_path, full_page=True,
                        clip={'x': 15, 'y': max(0, copilot_y - 10), 'width': 1250,
                              'height': next_section_y - copilot_y})

        browser.close()
        print(f"Saved: {overview_path}")
        print(f"Saved: {details_path}")
        return overview_path, details_path

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Capture metrics dashboard screenshots')
    parser.add_argument('--output-dir', default=os.path.expanduser('~/Downloads'),
                        help='Output directory for screenshots')
    args = parser.parse_args()
    capture(args.output_dir)
