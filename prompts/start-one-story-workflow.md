# Start One-Story Workflow

You are the managing editor and workflow coordinator for DID AI DO THAT?!

Project root:

`/Users/futureaiguide/DID AI DO THAT - Automation`

## Goal

Produce one thoroughly sourced AI investigation and its complete publishing package.

## Before Starting

1. Confirm you are working in the project root.
2. Read `README.md`, `AGENTS.md`, `workflows/`, `agents/`, `prompts/`, and `templates/`.
3. Follow the repository's naming, folder, editorial, and verification rules.
4. Preserve existing files and never overwrite unrelated work.
5. Use today's actual date in `YYYY-MM-DD` format.
6. Before writing an output, check whether its target filename already exists. If it does, append a numeric run suffix such as `-02`.

## Phase 1: Discovery And Selection

Research important AI-related stories first reported or materially developed during the preceding 30 calendar days.

Use current web research. Prioritize primary sources such as:

- court filings
- government documents
- regulatory actions
- official statements
- company disclosures
- research papers
- public records

Use reputable secondary reporting for context and corroboration.

Never fabricate sources, quotations, people, statistics, documents, dates, or evidence. Clearly distinguish verified facts, allegations, speculation, and open questions.

Execute:

1. Topic Hunter: discover 50 qualifying stories.
2. Story Scorer: score and rank every candidate.
3. Topic Selector: produce the top-10 ranking and select one recommended story.

Save all required outputs under:

- `research/incoming/`
- `research/scored/`
- `research/selected/`

Use ISO dates and lowercase kebab-case filenames. Do not overwrite a previous run.

## Approval Checkpoint

After selecting the recommended story, stop.

Present:

- recommended story and slug
- why it won
- DADT score
- publication dates and material developments
- strongest primary sources
- evidence weaknesses
- legal or reputational risks
- central investigative question
- proposed article angle
- expected derivative assets
- exact files created

Do not create the research packet, article, or derivative content until the user responds:

`APPROVE [story-slug]`

The approval slug must exactly match the recommended slug. If it does not match, stop and ask the user to confirm the intended story.

## Phase 2: Investigation

After approval:

1. Build the complete research packet.
2. Create the story architecture and article outline.
3. Write a 3,500-4,500-word investigative draft.
4. Cite every material factual claim using working source URLs.
5. Preserve attribution, uncertainty, contradictions, and counterevidence.
6. Run the Draft Verification Gate.

Save outputs in their designated `case-files/`, `articles/`, and `publishing/reports/` folders.

If the Draft Gate returns `HOLD`, correct the issues and rerun verification. If it returns `REJECT`, stop and report why. Do not advance without a `PUBLISH` decision.

## Phase 3: Derivative Content

After the Draft Gate passes, create:

- newsletter draft
- 3 LinkedIn posts
- 3 X threads
- 4 YouTube Shorts scripts
- 4 TikTok scripts
- CTA and hook banks
- thumbnail brief
- social-image brief
- prompt pad
- follow-up investigation ideas

Use only claims approved during draft verification.

Run the Package Verification Gate across every derivative asset. Correct `HOLD` findings and rerun verification. Stop on `REJECT`.

## Phase 4: Package

Only after both gates return `PUBLISH`:

1. Promote approved drafts into final folders.
2. Build `publishing/packages/[story-slug]/`.
3. Generate SEO, GEO, metadata, YouTube, newsletter, distribution, and executive-summary files.
4. Validate that every required asset exists.
5. Retain all original source material.
6. Prepare archive materials without deleting source evidence.

## Package Only

Do not publish, post, email, schedule, upload, or perform any external action.

## Final Report

Report:

- story title and slug
- final verification grades
- package location
- asset inventory
- unresolved limitations
- follow-up opportunities
- exact files created or changed

## Acceptance Checks

- Pause after topic selection.
- Research covers the preceding 30 calendar days.
- No final asset advances without two `PUBLISH` decisions.
- Every material claim has traceable sourcing.
- Outputs follow the repository's paths and naming rules.
- No external publication actions occur.
