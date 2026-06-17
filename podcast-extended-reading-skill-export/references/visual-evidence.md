# Visual Evidence

Read this file whenever the source contains important quantitative claims, comparative evidence, timelines, or figures.

This guidance borrows the most useful habits from the local `pdf` skill and the `literature-review` skill:

- from `pdf`: render first, inspect visually, do not trust raw text extraction for visual evidence
- from `literature-review`: use figures when they genuinely compress understanding rather than as decoration

Relevant local skill paths:

- `/Users/wangshihui/.codex/plugins/cache/openai-primary-runtime/pdf/26.614.11602/skills/pdf/SKILL.md`
- `/Users/wangshihui/.codex/skills/literature-review/SKILL.md`

## Default Rule

For quantitative sources, do not stop at a prose summary.

Always try to surface the evidence in this order:

1. `关键数据速览`
2. `对比表或小表格`
3. `必要时的关键图表`

In other words:

- numbers first
- compact comparison second
- extracted figure only when it adds speed or clarity

## What Counts As `关键数据`

Pull out the numbers that change interpretation, such as:

- sample size
- time window
- treatment vs control gap
- effect size
- accuracy / F1 / AUC / Sharpe / drawdown / hazard ratio
- improvement over baseline
- confidence interval or uncertainty range when available
- key dates, counts, and rates for historical material

Do not dump every number from the paper. Extract the `3-7` numbers that matter most.

## When To Extract A Figure

Extract or recreate a figure only when at least one of these is true:

- the result is easiest to understand visually
- the chart shows a pattern that prose would flatten
- the chart clarifies a comparison across time, groups, or conditions
- the chart reveals a limitation or instability that headline metrics hide

Typical good candidates:

- treatment vs control curves
- ablation charts
- event-study plots
- survival curves
- confusion matrices
- time-series breaks
- before/after comparisons
- market impact or regime charts
- historical timelines or maps

Avoid figure extraction when:

- the chart duplicates a simple numeric table
- labels are unreadable
- the figure is mostly decorative
- the provenance is unclear

## Preferred Extraction Order

1. Prefer native figure assets from official HTML, PMC, or JATS XML when available.
2. If native assets are unavailable, use the PDF route:
   - render the relevant PDF page to PNG
   - visually inspect the page
   - crop the figure cleanly
   - keep axis labels, legend, and figure caption reference readable
3. If extraction is messy but the figure matters, recreate a compact comparison table instead of forcing an unreadable image.

## Automatic Figure Script

Use the bundled fully automatic extractor before falling back to ad hoc handling:

```bash
python3 /Users/wangshihui/.codex/skills/podcast-extended-reading/scripts/extract_key_figures.py \
  paper.pdf \
  --top-k 3 \
  --save-page-previews
```

What it does:

- bootstraps `PyMuPDF` and `Pillow` automatically on first run
- scans the PDF for `Figure / Fig / Table / Chart / Exhibit / Panel` captions
- renders pages and infers candidate crop regions above or below the caption
- ranks candidates and exports crops plus a `manifest.json`

What to check after running it:

- whether the exported crop actually contains the intended chart or table
- whether the caption link is plausible
- whether one of the top-ranked candidates is enough, or whether a compact reconstructed table would still be clearer

## PDF Route

When the figure lives only in a PDF, follow the local `pdf` skill pattern:

- render first with `pdftoppm`
- inspect the resulting page image
- crop only the necessary figure area
- verify the output visually

Do not rely on text extraction alone for figure understanding.

## Figure Metadata

Whenever you include a figure, always write:

- `图表来源`: link to the original source
- `图表身份`: figure number, table number, or page number if available
- `这张图说明了什么`: one direct sentence stating the claim this visual is carrying
- `怎么读这张图`: `1-3` sentences on what to look at first
- `为什么它重要`: one sentence on why this visual accelerates understanding

## Obsidian Convention

If exporting into Obsidian and images are used:

- save images into a stable sibling assets folder, for example `assets/<note-slug>/`
- use Markdown image links pointing to the local asset
- keep filenames descriptive, such as `paper-1-figure-2.png`

## Reconstruction Rule

If the original figure cannot be cleanly extracted but the data relationship is simple:

- recreate a mini-table
- or recreate a very simple chart from the paper's reported numbers

If you recreate, say so explicitly. Do not present a reconstructed chart as if it were the paper's original image.

## Fast Visual Summary Template

Use this shape for quantitative sources:

- `关键数据`: `3-7` high-signal numbers
- `一句话结论`: the shortest faithful takeaway
- `关键图表`: include only if it beats prose
- `这张图说明了什么`: say the visual's main claim before interpretation
- `怎么读这张图`: tell the reader where to look first

The reader should be able to understand the evidence in under 30 seconds before reading the full interpretation.
