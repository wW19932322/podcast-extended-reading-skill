# Source Ladder

Use this file before searching for outside material.

## Priority Order

1. Peer-reviewed papers and official institutional publications
2. Strong preprints and working papers with clear methods and traceable authorship
3. Official archives, museums, libraries, standards bodies, and primary historical repositories
4. High-confidence reported articles with direct reporting or direct source use
5. Sourceable books only when there is a stable official page and the relevant point can be paraphrased responsibly without relying on opaque long excerpts

## What To Avoid

- unsourced summaries
- listicles and weak secondary rewrites
- long book citations that cannot be traced cleanly
- generic blog posts with no primary evidence
- claims that cannot be linked back to a stable source page

## Confidence Rubric

### High

Use `高` when most of these are true:

- the source is primary or close to primary
- the method or evidence base is clear
- the claim is well-scoped
- the source is established or corroborated by adjacent work

Typical examples:

- strong peer-reviewed paper
- official archive or institution page
- deeply sourced reporting with named evidence

### Medium

Use `中` when the source is useful but one or more things are weaker:

- the result is plausible but not heavily replicated
- the source is timely but still narrow
- the evidence is real but not decisive
- the source is high quality but not primary

Typical examples:

- good single-study paper
- strong feature article with limited direct data
- narrower domain paper with modest evidence scope

### Medium-Low

Use `中低` when the source is promising but still fragile:

- it is a new arXiv preprint
- the result depends heavily on one dataset or benchmark
- external validity is unclear
- implementation details may drive the apparent win

### Low

Use `低` sparingly. Only include such sources when they are uniquely informative and label the weakness clearly.

## Visual Evidence And Confidence

- A clean figure from a strong primary source can improve understanding, but it does not automatically raise the confidence rating.
- If the figure provenance is weak, labels are unclear, or the image had to be heavily reconstructed, say so explicitly.
- Never let an attractive chart disguise weak identification, weak sampling, or weak external validity.
- If a recreated table or chart is easier to trust than a messy extraction, prefer the reconstruction and label it clearly as reconstructed from reported numbers.

## Paper Review Checklist

For every paper, capture:

- `假设`: What question is the paper really asking?
- `实验/方法`: What data, model, experiment, identification strategy, or benchmark is used?
- `结果`: What did it actually find?
- `驳斥或修正`: Which simple story, baseline, or prior belief does it challenge?
- `研究本质`: What deeper mechanism, contrast, or way of seeing is the paper isolating beneath its specific dataset or task?
- `哲学式启发`: One short question or sentence that sharpens the conceptual stake without becoming empty prose.
- `局限性`: What should stop the reader from overusing the result?
- `置信度`: High / medium / medium-low / low, with one-sentence reason

## Non-Paper Review Checklist

For historical, archival, or reported sources, capture:

- `核心主张`: What is the source saying?
- `证据基础`: What material does it rely on?
- `为什么和播客原文相关`: Which anchor does it illuminate?
- `复杂化了什么`: Which simplistic interpretation does it complicate?
- `研究本质`: What pattern, lens, or structural lesson makes this source worth reading beyond the surface anecdote?
- `哲学式启发`: One short question or sentence that turns the item into a reflective hinge.
- `局限性`
- `置信度`

## Writing `研究本质`

Good `研究本质` paragraphs do not repeat the result in softer language. They should answer one of these:

- What is the source really isolating?
- What contrast makes the source meaningful?
- What hidden variable or structural relation does the source surface?
- What way of seeing becomes available after reading it?

Keep it short, usually `2-4` sentences.

## Writing `哲学式启发`

Good `哲学式启发` lines:

- arise from the source rather than from decoration
- preserve the truth conditions of the source
- sharpen the tension, boundary, or implication

Avoid:

- empty motivational lines
- grand claims with no connection to the evidence
- mystical rhetoric that outruns the source

## Timeliness Rule

- If the user asks for recent or frontier material, include fresh sources and verify dates.
- For technical or quant domains with good arXiv coverage, include at least `3` recent arXiv items when relevant.
- Do not let timeliness replace credibility. Pair frontier work with stronger anchors whenever possible.
