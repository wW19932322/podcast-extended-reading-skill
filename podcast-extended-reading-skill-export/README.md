# podcast-extended-reading

An installable Codex skill for turning podcast episodes into anchored extended reading.

It is designed for Xiaoyuzhou and similar podcast workflows where we do not want a loose summary only. The skill starts from transcript-backed anchor passages, expands outward into high-confidence reading, and then links the episode to user-chosen outside fields such as neuroscience, behavioral economics, consumer psychology, or quantitative trading.

## What It Does

- Extracts `4-8` anchor handles from the original podcast content
- Builds episode-anchored extended reading before doing cross-domain linking
- Links every new source back to a concrete podcast passage
- Decomposes papers into hypothesis, method, results, challenged view, limitations, confidence
- Adds `研究本质` and a short `哲学式启发`
- Supports beginner mode with analogy-first, learning-science-informed explanations
- Surfaces `关键数据` and `关键图表`
- Includes an automatic PDF figure extraction script for evidence-heavy reading notes

## Repository Layout

- `SKILL.md`: main skill instructions
- `agents/openai.yaml`: agent configuration
- `references/`: source ladder, output template, novice explanation patterns, visual evidence rules
- `scripts/extract_key_figures.py`: automatic figure and table extraction helper

## Installation

Clone or copy this folder into your Codex skills directory as:

`~/.codex/skills/podcast-extended-reading`

If you are using a skill installer workflow, point it at this repository and keep the folder name as `podcast-extended-reading`.

## Notes

- The figure extraction script bootstraps its own local dependencies on first run.
- The generated local dependency folder `scripts/_vendor/` is intentionally ignored by git.
- The skill is optimized for sourceable outputs with direct links rather than unsourceable long-form book summaries.
