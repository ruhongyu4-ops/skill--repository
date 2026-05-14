---
name: cgse-ai-newsletter
description: >
  This skill generates and sends the monthly SRDC CGSE "AI In Engineering" Newsletter.
  It should be used when the user asks to create, draft, or send the CGSE AI newsletter,
  AI engineering newsletter, or monthly newsletter. Handles live metrics capture,
  dynamic content sections, image sourcing, and Outlook-compatible HTML email delivery.
  Automated sends go only to hru@amd.com for manual forward; do not bulk-mail DLs unless the user explicitly requests it in that conversation.
metadata:
  version: "1.3.0"
  category: internal-comms
---

# SRDC CGSE AI In Engineering Newsletter

Generate the monthly AMD SRDC CGSE "AI In Engineering" newsletter with live metrics screenshots, dynamic content sections, and Outlook-compatible HTML email delivery.

## Distribution policy (mandatory)

**Do not send the newsletter to distribution lists or large BCC groups from automation.** Deliver **only** to **`hru@amd.com`** (plain `--to`, or `--bcc-only` with that single address). The editor forwards manually from Outlook.

- Treat any request to “send the newsletter” as **personal delivery only** unless the user **explicitly** says in that same conversation to mail the full audience (DLs + named contacts).
- Keep the historical canonical BCC list below **for reference when forwarding manually** — not for scripted bulk send unless explicitly ordered.

## Skill Base Directory

All asset paths are relative to: `~/.claude/skills/cgse-ai-newsletter/`

## Workflow

### Step 1: Gather Inputs

Prompt the user for the following. Any input not provided will use defaults or be omitted.

| Input | Required? | Description |
|-------|-----------|-------------|
| Month/Year | Yes | e.g., "Apr. 2026" |
| Use of AI Story | Yes | Who did what, a brief description, and a link (Confluence page) |
| Training info | Optional | Training link or placeholder text |
| Industry Trend links | Optional | 3-5 links with titles for the Industry Trend column |
| AMD AI links | Optional | Links for the AMD AI column |
| Optional sections | Optional | New tool intro, AI tool development, infra ideas (see `references/optional_sections.md`) |

### Step 2: Capture Live Metrics Screenshots

Run the bundled capture script to screenshot the dashboard:

```bash
python3 ~/.claude/skills/cgse-ai-newsletter/scripts/capture_metrics.py --output-dir ~/Downloads
```

This produces two images:
- `newsletter_img1_overview.png` - Adoption Rate & Active Rate (AI Code + NABU trend charts)
- `newsletter_img2_copilot.png` - Microsoft Copilot Rates & Actions

The script dynamically detects section boundaries via heading y-positions, so it adapts to dashboard layout changes. If the script fails or coordinates need adjustment, read the script source and patch as needed.

### Step 3: Download Content-Relevant Images

Run the bundled image download script for each image. Derive comma-separated keywords from the story/training content.

#### AI Story Image

```bash
python3 ~/.claude/skills/cgse-ai-newsletter/scripts/download_images.py \
  --keywords "DERIVED,FROM,STORY,CONTENT" \
  --output ~/Downloads/ai_story_img.jpg \
  --fallback ~/.claude/skills/cgse-ai-newsletter/assets/ai_story_img.jpg
```

Keyword examples by story topic:
- AI agents/automation: `ai,agent,automation,workflow`
- Data visualization: `data,analytics,dashboard,visualization`
- Code generation: `code,programming,software,developer`
- MCP/API integration: `api,integration,network,mcp`
- Hardware testing: `circuit,hardware,testing,semiconductor`

#### Training Image

```bash
python3 ~/.claude/skills/cgse-ai-newsletter/scripts/download_images.py \
  --keywords "DERIVED,FROM,TRAINING,TOPIC" \
  --output ~/Downloads/training_img.jpg \
  --fallback ~/.claude/skills/cgse-ai-newsletter/assets/training_img.jpg \
  --width 280 --height 190
```

Keyword examples by training topic:
- General AI training: `training,workshop,learning`
- Conference/presentation: `conference,presentation,workshop`
- Webinar/online: `webinar,training,learning`
- Hands-on lab: `training,code,programming`

The script tries multiple sources (Unsplash curated photos, Unsplash source redirect, loremflickr) and falls back to the bundled default image if all fail.

For **multi-modal / schedule** section images, prefer curated distinct photos (avoid two sections resolving to the same Unsplash id). You can run:

```bash
python3 ~/.claude/skills/cgse-ai-newsletter/scripts/fetch_multimodal_section_images.py --output-dir ~/Downloads
```

That writes `newsletter_multimodal_mar26.jpg` and `newsletter_multimodal2_mar26.jpg` (adjust filenames/month in HTML if needed). If the HTML uses **only one** image in that block, embed `multimodal_img` only.

### Step 4: Build the Newsletter HTML

1. Read the template from `assets/template.html`
2. Replace placeholders:
   - `{{MONTH_YEAR}}` - e.g., "Apr. 2026"
   - `{{AI_STORY_CONTENT}}` - Use of AI story HTML paragraphs
   - `{{TRAINING_CONTENT}}` - Training section content
   - `{{AMD_AI_LINKS}}` - AMD AI footer links
   - `{{INDUSTRY_TREND_LINKS}}` - Industry trend footer links
   - `{{OPTIONAL_NEW_TOOL_SECTION}}` - New tool intro HTML block, or empty string
   - `{{OPTIONAL_AI_TOOL_DEV_SECTION}}` - AI tool development HTML block, or empty string
   - `{{OPTIONAL_INFRA_SECTION}}` - Infrastructure ideas HTML block, or empty string
3. For optional sections, load the HTML patterns from `references/optional_sections.md` and fill in the tool/idea name and description
4. Write the final HTML to `~/Downloads/newsletter_<month>_<year>.html`

### Step 5: Send email (default — yourself only)

Use **`--to hru@amd.com`** (and **`--no-self-cc`**) with the final HTML and full **`--embed-image`** list. Subject line without `(PREVIEW)` when it is the handoff copy for manual forward.

**Option A — To header = you (default):**

```bash
python3 ~/.mutt/scripts/send_email.py \
  --from "dl.CGSE_AITools_Newsletter@amd.com" \
  --to "hru@amd.com" \
  --subject "SRDC CGSE AI In Engineering Newsletter - <Month>. <Year>" \
  --body-file ~/Downloads/newsletter_<month>_<year>.html \
  --html --no-self-cc \
  --recipient-log ~/Downloads/newsletter_recipient_audit.log \
  --embed-image newsletterlogo ~/.claude/skills/cgse-ai-newsletter/assets/newsletterlogo.png \
  --embed-image metrics_banner ~/.claude/skills/cgse-ai-newsletter/assets/metrics_banner.png \
  --embed-image metrics_overview ~/Downloads/newsletter_img1_overview.png \
  --embed-image metrics_details ~/Downloads/newsletter_img2_copilot.png \
  --embed-image statics_banner ~/.claude/skills/cgse-ai-newsletter/assets/statics_banner.jpg \
  --embed-image multimodal_img ~/Downloads/newsletter_multimodal_<month>_<year>.jpg \
  --embed-image internal_training_img ~/Downloads/newsletter_internal_training_<month>_<year>.jpg \
  --embed-image ai_story_img ~/Downloads/newsletter_ai_story_<month>_<year>.jpg \
  --embed-image training_img ~/Downloads/newsletter_training_<month>_<year>.jpg
```

Omit `--embed-image multimodal_img` / `internal_training_img` if that month’s HTML has no matching `cid:` (or if multi-modal uses only one image — omit the second file and any unused CID).

**Option B — BCC-only preview** (header `To` = From; **SMTP envelope** = that `To` address **plus** every `--bcc`, so the relay accepts the message — Exchange rejects “To without RCPT TO”):

Add `--bcc-only --bcc "hru@amd.com"` and **omit** `--to` (requires at least one `--bcc`).

If a downloaded image is missing, substitute the bundled fallback path (e.g. `~/.claude/skills/cgse-ai-newsletter/assets/ai_story_img.jpg`).

If optional sections include images (e.g., `new_tool_img`), add matching `--embed-image` lines.

### Step 6: Manual forward (human step)

After **`hru@amd.com`** receives the message, forward from Outlook to the real audience. **Reference list** (Mar 2026 — update when distribution changes):

- `ddl.sdong.all.employees@amd.com`
- `ddl.sdong.all.serviceproviders@amd.com`
- `dl.CDCPlatform_BIOS@amd.com`
- `Karen.Cheung@amd.com`
- `Kiran.Eastman@amd.com`
- `Rengith.Thomas@amd.com`
- `Tom.Dryburgh@amd.com`

Optional: append `--recipient-log ~/Downloads/newsletter_recipient_audit.log` on the **single-recipient** script send for a local audit trail.

**Bulk SMTP send is deprecated** unless the user clearly says in that turn to mail everyone; if they do, use `send_email.py` with `--bcc-only` / `--empty-to` only per their exact instructions and never substitute image paths without confirmation.

**Why BCC is not visible in received mail:** BCC is omitted from headers. For delivery verification at scale after a manual forward, use **Exchange message trace** (or your org’s equivalent).

## Static Assets (same every month)

| Asset | CID Name | File |
|-------|----------|------|
| Header logo | `newsletterlogo` | `assets/newsletterlogo.png` |
| Tool metrics banner | `metrics_banner` | `assets/metrics_banner.png` |
| Statics banner | `statics_banner` | `assets/statics_banner.jpg` |

## Dynamic Assets (generated each month)

| Asset | CID Name | Source |
|-------|----------|--------|
| Metrics overview | `metrics_overview` | Screenshot via `scripts/capture_metrics.py` |
| Metrics details | `metrics_details` | Screenshot via `scripts/capture_metrics.py` |
| Multi-modal section | `multimodal_img` | `scripts/fetch_multimodal_section_images.py` or `download_images.py` with distinct document/schedule keywords |
| Internal training block | `internal_training_img` | `scripts/download_images.py` with training/workshop keywords |
| AI story image | `ai_story_img` | `scripts/download_images.py` with story keywords (fallback: `assets/ai_story_img.jpg`) |
| Training image | `training_img` | `scripts/download_images.py` with training keywords (fallback: `assets/training_img.jpg`) |

## Optional Sections

Inserted between the metrics and the Use of AI story section. Include only when the user provides content. Load HTML patterns from `references/optional_sections.md`.

Available section types:
- **New Tool Introduction** - For introducing a new AI tool to the team
- **AI Tool Development** - For showcasing internally developed AI tools or updates
- **Infrastructure Ideas** - For sharing infrastructure-level ideas (MCP gateway, skill marketplace, shared MCP servers, etc.)

## HTML Formatting Rules

- **Outlook-compatible**: Table-based layout only, 709px (532pt) width, MSO/Word HTML format with VML namespaces
- **Fonts**: Arial for all content text, Klavika Regular for special headings
- **Colors**: Black header, white body sections, `#467886` for links
- **Images**: All images MUST use CID embedding (not base64, not external URLs) for Outlook compatibility
- **Full-width banners**: Apply `display:block;margin:0;padding:0` on `<img>` and `font-size:0;line-height:0` on `<td>` to eliminate gaps
- **CTA arrows**: Use `https://discover.amd.com/rs/885-ZYT-361/images/internal-newsletter-CTA-arrow.png` for link arrows
- **Footer link format**: `&raquo;` bullet before each link

## Confluence Integration

For Use of AI stories, create a detailed Confluence page under the parent "Use Of AI Stories" page:
- Space: `SRDCV`
- Parent page ID: `1171912595`
- URL: `https://amd.atlassian.net/wiki/spaces/SRDCV/pages/1171912595/Use+Of+AI+Stories`

Use the MCP Atlassian tools (`mcp__cloud_atlassian__confluence_create_page`) to create the page, then link it from the newsletter.

## Email Infrastructure

- **SMTP**: AMD internal relay `ATLSMTP10.amd.com:25` (no auth, internal network only)
- **Send script**: `~/.mutt/scripts/send_email.py`
- **Key flags**: `--html`, `--embed-image CID FILEPATH`, `--from`, `--no-self-cc`, `--to` (default delivery), `--bcc-only` + single `--bcc` if needed, `--recipient-log PATH`. **`--bcc-only` with more than one BCC address is rejected unless `--confirm-bulk-bcc`** (stops accidental DL blasts / duplicate copies).
- **From address**: `dl.CGSE_AITools_Newsletter@amd.com`
- **Contact DL**: `dl.SRDC_CGSE_AIInEngineering_Newsletter`
- **Note**: Script SMTP does not populate your personal Outlook **Sent Items**; use `--sent-folder-copy` to your mailbox for an Inbox archive, plus `--recipient-log` for a local audit trail.

## Previous Newsletters for Reference

- Jan 2026, Feb 2026, Mar 2026 newsletters are in `~/Downloads/` as `.html` or `.msg` files
- Mar 2026 final version: `~/Downloads/newsletter_march_2026.html`
