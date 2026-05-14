#!/usr/bin/env python3
"""
Download content-relevant images for the newsletter.

Derives search keywords from the provided content description and tries
multiple image sources in order until one succeeds.

Usage:
    python3 download_images.py --keywords "AI,agent,automation" --output ~/Downloads/ai_story_img.jpg
    python3 download_images.py --keywords "workshop,training" --output ~/Downloads/training_img.jpg
    python3 download_images.py --keywords "AI,agent" --output ~/Downloads/ai_story_img.jpg --fallback ~/.claude/skills/cgse-ai-newsletter/assets/ai_story_img.jpg

Options:
    --keywords    Comma-separated search keywords derived from content
    --output      Output file path for the downloaded image
    --fallback    Fallback image path if all downloads fail
    --width       Image width (default: 280)
    --height      Image height (default: 210)
"""

import argparse
import os
import shutil
import sys
import urllib.request


def try_loremflickr(keywords, width, height, output_path):
    """Primary source: loremflickr.com (Creative Commons photos from Flickr).
    Supports keyword-based search, no auth required."""
    url = f'https://loremflickr.com/{width}/{height}/{keywords}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = resp.read()
        if len(data) < 1000:
            raise ValueError(f"Image too small ({len(data)} bytes)")
        with open(output_path, 'wb') as f:
            f.write(data)
        return len(data)


def try_unsplash_source(keywords, width, height, output_path):
    """Fallback: Unsplash source redirect (may be unreliable)."""
    search_term = keywords.replace(',', '-')
    url = f'https://source.unsplash.com/{width}x{height}/?{search_term}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = resp.read()
        if len(data) < 1000:
            raise ValueError(f"Image too small ({len(data)} bytes)")
        with open(output_path, 'wb') as f:
            f.write(data)
        return len(data)


def try_unsplash_direct(keywords, width, height, output_path):
    """Primary source: Unsplash direct image URL with curated photo IDs.
    Maps content categories to high-quality, relevant Unsplash photos."""
    keyword_lower = keywords.lower()

    # Curated photo IDs by content category (verified working)
    # Each category has multiple options; the first match wins
    photo_map = {
        # AI / Machine Learning
        'ai':            'photo-1677442136019-21780ecad995',  # AI brain visualization
        'llm':           'photo-1677442136019-21780ecad995',  # AI brain
        'agent':         'photo-1620712943543-bcc4688e7485',  # AI humanoid face
        'chatbot':       'photo-1620712943543-bcc4688e7485',  # AI face
        'machine learning': 'photo-1555255707-c07966088b7b',  # neural network
        # Automation / Workflow
        'automation':    'photo-1531746790095-e6b1258a235e',  # automated process
        'workflow':      'photo-1531746790095-e6b1258a235e',  # process flow
        'robot':         'photo-1485827404703-89b55fcc595e',  # robot
        'pipeline':      'photo-1558494949-ef010cbdcc31',     # connected nodes
        # Code / Development
        'code':          'photo-1555066931-4365d14bab8c',     # code on screen
        'programming':   'photo-1461749280684-dccba630e2f6',  # programming
        'software':      'photo-1555066931-4365d14bab8c',     # code
        'developer':     'photo-1461749280684-dccba630e2f6',  # dev environment
        'script':        'photo-1555066931-4365d14bab8c',     # code
        # Data / Analytics
        'data':          'photo-1551288049-bebda4e38f71',     # data dashboard
        'analytics':     'photo-1551288049-bebda4e38f71',     # analytics
        'dashboard':     'photo-1551288049-bebda4e38f71',     # dashboard
        'visualization': 'photo-1551288049-bebda4e38f71',     # charts
        'report':        'photo-1551288049-bebda4e38f71',     # data report
        # Schedule / timeline (distinct from generic dashboard — monitor + bar chart)
        'timeline':      'photo-1686061592689-312bbfb5c055',
        'schedule':      'photo-1686061592689-312bbfb5c055',
        'gantt':         'photo-1686061592689-312bbfb5c055',
        'planning':      'photo-1686061592689-312bbfb5c055',
        # Documents / multi-modal inputs (desk, papers, whiteboard — not AI brain default)
        'documents':     'photo-1566699270403-3f7e3f340664',
        'paperwork':     'photo-1566699270403-3f7e3f340664',
        'pdf':           'photo-1566699270403-3f7e3f340664',
        'files':         'photo-1566699270403-3f7e3f340664',
        # Training / Education
        'training':      'photo-1524178232363-1fb2b075b655',  # classroom training
        'workshop':      'photo-1540575467063-178a50c2df87',  # conference/workshop
        'presentation':  'photo-1540575467063-178a50c2df87',  # presentation
        'conference':    'photo-1540575467063-178a50c2df87',  # conference hall
        'webinar':       'photo-1588196749597-9ff075ee6b5b',  # video call
        'learning':      'photo-1524178232363-1fb2b075b655',  # learning
        'tutorial':      'photo-1524178232363-1fb2b075b655',  # teaching
        # Infrastructure / Networking
        'network':       'photo-1558494949-ef010cbdcc31',     # network nodes
        'api':           'photo-1558494949-ef010cbdcc31',     # API connections
        'integration':   'photo-1558494949-ef010cbdcc31',     # integration
        'mcp':           'photo-1558494949-ef010cbdcc31',     # protocol/network
        'server':        'photo-1558494949-ef010cbdcc31',     # server
        'gateway':       'photo-1558494949-ef010cbdcc31',     # gateway
        'infrastructure': 'photo-1558494949-ef010cbdcc31',    # infra
        # Hardware / Electronics
        'circuit':       'photo-1518770660439-4636190af475',  # circuit board
        'hardware':      'photo-1518770660439-4636190af475',  # hardware
        'chip':          'photo-1518770660439-4636190af475',  # chip/circuit
        'semiconductor': 'photo-1518770660439-4636190af475',  # semiconductor
        'testing':       'photo-1581091226825-a6a2a5aee158',  # lab testing
        'validation':    'photo-1581091226825-a6a2a5aee158',  # validation
        # Collaboration / Teamwork
        'collaboration': 'photo-1522071820081-009f0129c71c',  # team collaboration
        'teamwork':      'photo-1522071820081-009f0129c71c',  # teamwork
        'meeting':       'photo-1522071820081-009f0129c71c',  # meeting
    }

    # Find the best matching photo ID based on keyword order
    photo_id = None
    for kw in keyword_lower.split(','):
        kw = kw.strip()
        if kw in photo_map:
            photo_id = photo_map[kw]
            break

    # Fallback: check if any keyword appears as substring
    if not photo_id:
        for term, pid in photo_map.items():
            if term in keyword_lower:
                photo_id = pid
                break

    if not photo_id:
        photo_id = 'photo-1677442136019-21780ecad995'  # default AI image

    url = f'https://images.unsplash.com/{photo_id}?w={width}&h={height}&fit=crop'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = resp.read()
        if len(data) < 1000:
            raise ValueError(f"Image too small ({len(data)} bytes)")
        with open(output_path, 'wb') as f:
            f.write(data)
        return len(data)


def download_image(keywords, output_path, fallback_path=None, width=280, height=210):
    """Download a content-relevant image using multiple sources.

    Tries sources in order:
    1. Unsplash direct photo URL (curated by category, most reliable + relevant)
    2. Unsplash source redirect (keyword-based, sometimes unreliable)
    3. loremflickr.com (keyword-based, Creative Commons, hit-or-miss relevance)
    4. Local fallback asset (guaranteed)
    """
    output_path = os.path.expanduser(output_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    sources = [
        ('unsplash_direct', try_unsplash_direct),
        ('unsplash_source', try_unsplash_source),
        ('loremflickr', try_loremflickr),
    ]

    for name, func in sources:
        try:
            size = func(keywords, width, height, output_path)
            print(f"Downloaded from {name}: {size} bytes -> {output_path}")
            return True
        except Exception as e:
            print(f"  {name} failed: {e}")

    # All sources failed - use fallback
    if fallback_path:
        fallback_path = os.path.expanduser(fallback_path)
        if os.path.exists(fallback_path):
            shutil.copy2(fallback_path, output_path)
            print(f"Used fallback: {fallback_path} -> {output_path}")
            return True
        else:
            print(f"Fallback not found: {fallback_path}")

    print("ERROR: All image sources failed and no fallback available")
    return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download content-relevant newsletter images')
    parser.add_argument('--keywords', required=True,
                        help='Comma-separated search keywords (e.g., "AI,agent,automation")')
    parser.add_argument('--output', required=True,
                        help='Output file path')
    parser.add_argument('--fallback', default=None,
                        help='Fallback image path if all downloads fail')
    parser.add_argument('--width', type=int, default=280,
                        help='Image width (default: 280)')
    parser.add_argument('--height', type=int, default=210,
                        help='Image height (default: 210)')
    args = parser.parse_args()

    success = download_image(args.keywords, args.output, args.fallback,
                             args.width, args.height)
    sys.exit(0 if success else 1)
