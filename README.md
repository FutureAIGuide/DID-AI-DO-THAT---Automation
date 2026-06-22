# DID AI DO THAT?! Automation

This repository defines the editorial agents, prompts, workflows, templates, and output folders used to produce evidence-based AI investigations.

## Quick Start

Start a complete one-story run with:

`prompts/start-one-story-workflow.md`

Paste the full prompt into a new Codex thread opened at this project root. The workflow researches the preceding 30 days, pauses after selecting one story, and continues only after receiving `APPROVE [story-slug]`.


## Automation

This repository now includes GitHub Actions workflows in `.github/workflows/` for OpenRouter-driven discovery, story production, weekly runs, and publish-package validation.

### Required GitHub Secrets And Variables

- `OPENROUTER_API_KEY` (secret, required)
- `OPENROUTER_MODEL` (repository variable, optional fallback model)
- `OPENROUTER_SITE_URL` (repository variable, optional)
- `OPENROUTER_SITE_NAME` (repository variable, optional)

A local example is provided in `.env.example`.

### Workflow Files

- `daily-discovery.yml` — scheduled daily at 13:15 UTC plus manual discovery, scoring, and selection
- `story-production.yml` — builds one approved story from research packet through publishing package
- `weekly-production.yml` — scheduled Mondays at 14:30 UTC to run discovery and then produce the selected weekly stories
- `publish-pipeline.yml` — validates completed packages and mirrors approved packages into `archive/`

### Notes

- Models that support current-web research through OpenRouter are recommended for the strongest discovery results.
- Every workflow writes repository assets using the existing folder ownership and naming rules.
- Verification gates still block downstream publishing-package steps when a report returns `HOLD` or `REJECT`.

## Workflow

1. Topic Hunter discovers candidate stories.
2. Story Scorer ranks the candidates.
3. Topic Selector chooses the investigation.
4. Investigator builds the sourced research packet.
5. Story Architect creates the article outline.
6. Draft Builder writes the investigation.
7. Verifier runs the draft gate for claims, citations, and risk.
8. Newsletter, social, visual, and prompt-pad builders create derivative assets.
9. Verifier runs the package gate across all derivative assets.
10. Publisher promotes approved drafts to final and builds the publishing package.
11. The publish pipeline validates the complete package.
12. Completed assets are archived.

No verification or approval step may be skipped.

## Directory Guide

| Path | Purpose |
| --- | --- |
| `agents/` | Role definitions and operating rules |
| `prompts/` | Reusable task prompts |
| `workflows/` | End-to-end operating procedures |
| `templates/` | Blank output templates |
| `research/` | Incoming, scored, and selected story candidates |
| `case-files/` | Active and approved investigation packets |
| `articles/` | Article outlines, drafts, and final copy |
| `newsletter/` | Newsletter outlines, drafts, and final copy |
| `social/` | LinkedIn and X assets |
| `video/` | Shorts and TikTok scripts |
| `assets/` | Screenshots, social images, and thumbnails |
| `prompt-pads/` | Reusable prompt collections by story |
| `publishing/` | Verification reports, packages, and executive summaries |
| `archive/` | Completed story asset collections |

## Naming Rules

- Use lowercase kebab-case for files and folders.
- Use a stable story slug for every asset: `[story-name]`.
- Use ISO dates for discovery runs: `YYYY-MM-DD`.
- Use `.md` for editorial text and workflow documents.
- Keep templates in `templates/`, never in output folders.
- Do not commit `.DS_Store` or other operating-system metadata.

## Story Asset Examples

- `research/incoming/2026-06-22-story-discovery.md`
- `case-files/active/example-story-research-packet.md`
- `articles/outlines/example-story-outline.md`
- `articles/drafts/example-story-draft.md`
- `articles/final/example-story.md`
- `publishing/reports/example-story-draft-verification-report.md`
- `publishing/reports/example-story-package-verification-report.md`
- `publishing/packages/example-story/`

## Editorial Gate

Only content receiving `PUBLISH` decisions at both verification gates may move into final and publishing folders. A `HOLD` decision requires corrections and another review. A `REJECT` decision stops publication.
