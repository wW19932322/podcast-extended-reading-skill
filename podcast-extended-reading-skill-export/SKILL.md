---
name: podcast-extended-reading
description: Create anchored extended reading from a podcast or Xiaoyuzhou episode by first extracting transcript-based anchor passages, then finding high-confidence follow-up reading across papers, history, reported articles, and sourceable books, and finally linking the episode to a user-chosen outside field. Use when the user asks for 播客延展阅读, 跨领域 link, 论文/历史/文章/书籍延伸, anchored source notes, or a research-style companion note tied to a podcast transcript or episode link.
---

# Podcast Extended Reading

## Workflow

1. Prepare the source episode.
2. Extract anchor handles from the original episode text.
3. Produce a first-pass extended reading around the episode itself.
4. Ask the user which outside field to link and whether they are a beginner in that field.
5. Produce a second-pass cross-domain reading tied back to the episode anchors.
6. Export or place the result where the user wants if they ask for Obsidian or another note destination.

## Step 1: Prepare The Source Episode

- If the source is a Xiaoyuzhou link, local podcast audio, transcript, or ASR JSON, read `/Users/wangshihui/.codex/skills/xiaoyuzhou-transcribe-summary/SKILL.md` fully and use that workflow first.
- Reuse an existing transcript when the user already supplied one.
- Do not invent transcript text, timestamps, or quotes.
- Preserve core metadata when available: episode title, show name, guests, source URL, publish date, duration, transcript quality.

## Step 2: Extract Anchor Handles

- Build `4-8` anchor handles from the original episode before searching for outside material.
- Each anchor handle must contain:
  - a short anchor title
  - a timestamp or location in the episode when available
  - a short original excerpt from the episode
  - one sentence on why this anchor matters
- Keep original excerpts short. Use them as retrieval handles, not as long quotations.
- Prefer anchors that are conceptually rich, not just catchy. Good anchors are claims, examples, paradoxes, metaphors, or moments where the speakers redefine the problem.

Typical anchor types:

- a core claim
- a vivid example
- a hidden assumption
- a definition shift
- a design or behavioral mechanism
- a philosophical or ethical conclusion

## Step 3: Produce The First-Pass Extended Reading

- Read `references/source-ladder.md` before gathering outside material.
- Read `references/output-template.md` before writing the final extended reading.
- Read `references/visual-evidence.md` whenever the outside material contains quantitative claims, comparisons, or figures worth extracting.
- Cover `2-5` major threads from the episode rather than spraying many weak links.
- Prefer sourceable materials with stable URLs. Good categories include:
  - peer-reviewed papers
  - high-quality preprints or working papers
  - official archives, institutions, museums, or standards bodies
  - high-confidence reported features or essays with clear sourcing
  - sourceable books only when there is an official landing page and the point can be tied to traceable excerpts or secondary primary reporting

Source selection rules:

- Prefer primary sources whenever possible.
- Prefer direct links to the paper, archive page, institution page, or official article.
- Avoid building key claims on long, hard-to-trace book passages.
- If a book is relevant but hard to source cleanly, use it as context only and base the written analysis on sourceable supporting material.

For every extended-reading item, explicitly link it back to one or more episode anchors and explain why the match is meaningful.
For every extended-reading item, also add:

- a short `研究本质` paragraph that says what deeper mechanism, contrast, or way of seeing the source is really isolating
- a one-sentence `哲学式启发` that turns the item into a sharper question, tension, or reflective prompt rather than a decorative slogan
- a `关键数据` subsection whenever the source contains numbers that materially change understanding
- a `关键图表` block when a chart, table, or figure will help the reader grasp the result faster than prose alone

When a paper PDF contains important visuals, use the bundled script for fully automatic extraction:

```bash
python3 /Users/wangshihui/.codex/skills/podcast-extended-reading/scripts/extract_key_figures.py \
  paper.pdf \
  --top-k 3 \
  --save-page-previews
```

The script bootstraps its own Python dependencies, finds likely `Figure/Fig/Table` captions, renders the PDF, infers crop regions automatically, and exports ranked candidate visuals plus a JSON manifest.

## Step 4: Ask The User For Cross-Domain Linking

After the first-pass extended reading, ask two short questions unless the user already answered them:

1. Which outside field should the episode be linked to?
2. In that field, are they a beginner, somewhat familiar, or advanced?

Use concise wording such as:

- `你想把这期播客继续 link 到哪个领域？`
- `你在这个领域算初学者、熟悉，还是已经会专业使用？`

Do not ask extra broad questions unless the task is genuinely blocked.

## Step 5: Produce The Cross-Domain Reading

- Build the second-pass reading around the user-chosen field, not around a generic analogy.
- Tie every cross-domain section back to a specific episode anchor.
- Quote the short original episode excerpt again inside the cross-domain section so the reader can see the bridge.
- State explicitly why that anchor and that outside source belong together.

If the user is a beginner in the target field:

- read `references/novice-explanation-patterns.md` before writing
- add more first-principles explanation
- define key terms before using them
- keep the explanation detailed without losing professional precision
- avoid talking down to the user
- add more analogies, but keep them structurally faithful
- state what each analogy maps onto and where it breaks
- prefer the sequence `worked example -> comparison -> abstraction -> formal restatement`
- when a concept is difficult, use `concrete case -> intermediate mapping -> abstract concept` rather than jumping straight to jargon
- end important subsections with a short self-explanation prompt that helps the reader test whether they really got the mechanism

If the user is already familiar or advanced:

- compress basics
- move faster into assumptions, model structure, debates, and edge cases

For fields with meaningful arXiv coverage:

- include at least `3` recent arXiv papers to preserve timeliness
- clearly mark them as preprints
- lower confidence relative to mature peer-reviewed work unless there is strong corroboration

If arXiv coverage is naturally weak in the chosen field:

- say that explicitly
- include the closest relevant arXiv items if they exist
- then use the strongest available alternative primary sources

## Decomposition Standards

Use the correct decomposition shape for each source type.

For papers:

- summarize the hypothesis or research question
- summarize the data, experiment, or method
- summarize the main result
- state what view, simplification, or prior belief the paper challenges
- extract the most decision-relevant numeric evidence into a compact `关键数据` block
- extract or recreate a key figure when it materially improves comprehension and can be sourced cleanly
- add a `研究本质` paragraph
- add a one-sentence `哲学式启发`
- state the limitations
- give a confidence rating

For historical or archive material:

- summarize the claim or historical lesson
- state what evidence the source relies on
- explain what simplistic story it complicates or corrects
- surface dates, counts, comparisons, or timelines in a compact `关键数据` block when useful
- include a timeline table, archival figure, map, or sourced visual only when it accelerates understanding
- add a `研究本质` paragraph
- add a one-sentence `哲学式启发`
- state the limitations
- give a confidence rating

For high-confidence reported articles:

- summarize the core claim
- state what reporting or evidence base supports it
- explain why it matters to the episode anchor
- pull out the concrete numbers, sample sizes, dates, or comparative facts instead of leaving them buried in prose
- include a visual only when the article's own sourced chart or a faithful reconstruction materially helps
- add a `研究本质` paragraph
- add a one-sentence `哲学式启发`
- state the limitations
- give a confidence rating

For sourceable books:

- use them only when there is a stable official or sourceable page
- summarize the thesis in a traceable way
- explain why the book belongs with the anchor
- if the relevant insight depends on a sequence, chronology, or typology, convert it into a compact comparison table
- add a `研究本质` paragraph
- add a one-sentence `哲学式启发`
- state the limits of using a book page versus the full text
- give a confidence rating

## Quality Checks

- Verify every new outside item points back to at least one episode anchor.
- Verify every cross-domain section repeats the relevant original episode excerpt.
- Separate source-grounded facts from your own synthesis.
- Mark frontier arXiv work as preprint status rather than presenting it as settled.
- Avoid shallow summaries. Each item should say what the source assumed, how it argued, what it found, what it pushes back against, and where it is weak.
- Verify every item contains both `研究本质` and `哲学式启发`.
- Verify every quantitative source surfaces its key numbers directly rather than hiding them in a paragraph.
- Verify every extracted figure has a source link, figure identity, and a short `怎么读这张图` note.
- In beginner mode, verify analogies are used to illuminate structure rather than replace structure.
- Use exact dates when freshness matters.
- If a source cannot be traced cleanly, do not use it as a core pillar.

## Optional Note Export

- If the user wants the deliverable in Obsidian, place the extended reading as a sibling or child note rather than burying it inside the transcript unless they explicitly ask for one merged file.
- Reuse the user's existing vault conventions when they already have a podcast note structure.
