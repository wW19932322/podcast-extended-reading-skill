#!/usr/bin/env python3
"""Automatically extract likely key figures/tables from a PDF.

This script is designed for the podcast-extended-reading skill:
- bootstrap its own Python dependencies on first run
- detect figure/table captions
- render PDF pages automatically
- infer crop regions above/below captions
- rank and export the most likely key visuals
"""

from __future__ import annotations

import argparse
import importlib
import json
import math
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


SCRIPT_DIR = Path(__file__).resolve().parent
VENDOR_DIR = SCRIPT_DIR / "_vendor"
CAPTION_RE = re.compile(
    r"^\s*(figure|fig\.?|table|chart|exhibit|panel)\s*([0-9]+[A-Za-z]?|[IVXLC]+)?[\s\.\:\-].*",
    re.IGNORECASE | re.DOTALL,
)


def _bootstrap_dependencies() -> None:
    VENDOR_DIR.mkdir(parents=True, exist_ok=True)
    install_cmd = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        "--quiet",
        "--target",
        str(VENDOR_DIR),
        "PyMuPDF>=1.24.0",
        "Pillow>=10.0.0",
    ]
    subprocess.run(install_cmd, check=True)


def ensure_dependencies() -> None:
    sys.path.insert(0, str(VENDOR_DIR))
    try:
        __import__("fitz")
        __import__("PIL")
        return
    except ModuleNotFoundError:
        pass

    _bootstrap_dependencies()
    if str(VENDOR_DIR) not in sys.path:
        sys.path.insert(0, str(VENDOR_DIR))
    importlib.invalidate_caches()
    __import__("fitz")
    __import__("PIL")


ensure_dependencies()

import fitz  # type: ignore  # noqa: E402
from PIL import Image  # type: ignore  # noqa: E402


@dataclass
class CaptionBlock:
    page_index: int
    page_number: int
    label: str
    key: str
    text: str
    bbox_pdf: tuple[float, float, float, float]


@dataclass
class CandidateRegion:
    page_index: int
    page_number: int
    caption_label: str
    caption_key: str
    caption_text: str
    direction: str
    bbox_pdf: tuple[float, float, float, float]
    bbox_px: tuple[int, int, int, int]
    score: float
    reason: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Automatically extract likely key figures/tables from a PDF."
    )
    parser.add_argument("pdf", help="Path to the source PDF")
    parser.add_argument(
        "--out-dir",
        default=None,
        help="Directory to write cropped figures into. Defaults to <pdf stem>_figures.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Number of top-ranked figures to export",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=180,
        help="Render DPI for page rasterization",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=0,
        help="Process at most this many pages from the start; 0 means all pages",
    )
    parser.add_argument(
        "--save-page-previews",
        action="store_true",
        help="Also save the rendered full page for each exported crop",
    )
    parser.add_argument(
        "--summary-json",
        default=None,
        help="Optional path to write a JSON summary manifest",
    )
    return parser.parse_args()


def normalize_text(text: str) -> str:
    return " ".join(text.replace("\n", " ").split())


def strip_caption_prefix(text: str) -> str:
    text = normalize_text(text)
    if ":" in text:
        return text.split(":", 1)[1].strip()
    return CAPTION_RE.sub("", text).strip() or text


def sentence_case(text: str) -> str:
    text = text.strip()
    if not text:
        return text
    return text[0].upper() + text[1:]


def summarize_visual(candidate: CandidateRegion) -> str:
    body = sentence_case(strip_caption_prefix(candidate.caption_text).rstrip("."))
    if candidate.caption_label == "table":
        return f"这张表主要说明：{body}。"
    if candidate.caption_label in {"figure", "fig", "fig.", "chart", "panel"}:
        return f"这张图主要说明：{body}。"
    return f"这条视觉证据主要说明：{body}。"


def rect_intersection_area(
    a: tuple[float, float, float, float],
    b: tuple[float, float, float, float],
) -> float:
    x0 = max(a[0], b[0])
    y0 = max(a[1], b[1])
    x1 = min(a[2], b[2])
    y1 = min(a[3], b[3])
    if x1 <= x0 or y1 <= y0:
        return 0.0
    return (x1 - x0) * (y1 - y0)


def collect_captions(page: fitz.Page, page_index: int) -> list[CaptionBlock]:
    captions: list[CaptionBlock] = []
    text_dict = page.get_text("dict")
    for block in text_dict.get("blocks", []):
        if block.get("type") != 0:
            continue
        spans: list[str] = []
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                spans.append(span.get("text", ""))
        block_text = normalize_text(" ".join(spans))
        if not block_text:
            continue
        if not CAPTION_RE.match(block_text):
            continue
        label_match = re.match(r"^\s*(figure|fig\.?|table|chart|exhibit|panel)", block_text, re.I)
        label = (label_match.group(1) if label_match else "figure").lower()
        key_match = re.match(
            r"^\s*(figure|fig\.?|table|chart|exhibit|panel)\s*([0-9]+[A-Za-z]?|[IVXLC]+)?",
            block_text,
            re.I,
        )
        label_token = (key_match.group(1) if key_match else label).lower().replace(".", "")
        number_token = (key_match.group(2) if key_match and key_match.group(2) else "na").lower()
        captions.append(
            CaptionBlock(
                page_index=page_index,
                page_number=page_index + 1,
                label=label,
                key=f"{label_token}-{number_token}",
                text=block_text,
                bbox_pdf=tuple(block.get("bbox", (0, 0, 0, 0))),  # type: ignore[arg-type]
            )
        )
    return captions


def collect_graphic_rects(page: fitz.Page) -> list[tuple[float, float, float, float]]:
    rects: list[tuple[float, float, float, float]] = []
    text_dict = page.get_text("dict")
    for block in text_dict.get("blocks", []):
        if block.get("type") == 1:
            rects.append(tuple(block.get("bbox", (0, 0, 0, 0))))  # type: ignore[arg-type]
    try:
        for drawing in page.get_drawings():
            rect = drawing.get("rect")
            if rect is not None:
                rects.append((rect.x0, rect.y0, rect.x1, rect.y1))
    except Exception:
        pass
    return rects


def render_page(page: fitz.Page, dpi: int) -> tuple[Image.Image, Image.Image]:
    pix = page.get_pixmap(dpi=dpi, alpha=False)
    mode = "RGB" if pix.n >= 3 else "L"
    img = Image.frombytes(mode, (pix.width, pix.height), pix.samples)
    gray = img.convert("L")
    return img, gray


def pdf_to_px(page_rect: fitz.Rect, bbox_pdf: tuple[float, float, float, float], img_w: int, img_h: int) -> tuple[int, int, int, int]:
    scale_x = img_w / page_rect.width
    scale_y = img_h / page_rect.height
    x0 = max(0, int(bbox_pdf[0] * scale_x))
    y0 = max(0, int(bbox_pdf[1] * scale_y))
    x1 = min(img_w, int(math.ceil(bbox_pdf[2] * scale_x)))
    y1 = min(img_h, int(math.ceil(bbox_pdf[3] * scale_y)))
    return x0, y0, x1, y1


def px_to_pdf(page_rect: fitz.Rect, bbox_px: tuple[int, int, int, int], img_w: int, img_h: int) -> tuple[float, float, float, float]:
    scale_x = page_rect.width / img_w
    scale_y = page_rect.height / img_h
    return (
        bbox_px[0] * scale_x,
        bbox_px[1] * scale_y,
        bbox_px[2] * scale_x,
        bbox_px[3] * scale_y,
    )


def compute_row_density(gray: Image.Image, threshold: int = 245) -> list[float]:
    w, h = gray.size
    px = gray.load()
    densities: list[float] = []
    for y in range(h):
        dark = 0
        for x in range(w):
            if px[x, y] < threshold:
                dark += 1
        densities.append(dark / max(1, w))
    return densities


def compute_col_density(gray: Image.Image, top: int, bottom: int, threshold: int = 245) -> list[float]:
    w, _ = gray.size
    px = gray.load()
    densities: list[float] = []
    span = max(1, bottom - top)
    for x in range(w):
        dark = 0
        for y in range(top, bottom):
            if px[x, y] < threshold:
                dark += 1
        densities.append(dark / span)
    return densities


def find_band(
    row_density: list[float],
    anchor_top: int,
    anchor_bottom: int,
    direction: str,
    page_height: int,
) -> tuple[int, int] | None:
    row_threshold = 0.01
    max_gap = max(8, int(page_height * 0.015))
    content_found = False
    gap = 0
    if direction == "above":
        indices = range(anchor_top - 1, -1, -1)
    else:
        indices = range(anchor_bottom, len(row_density))

    band_start = None
    band_end = None
    for idx in indices:
        dense = row_density[idx] >= row_threshold
        if not content_found:
            if dense:
                content_found = True
                band_start = idx
                band_end = idx
                gap = 0
            else:
                gap += 1
                if gap > max_gap:
                    break
            continue

        if dense:
            gap = 0
            if direction == "above":
                band_start = idx
            else:
                band_end = idx
        else:
            gap += 1
            if gap > max_gap:
                break

    if band_start is None or band_end is None:
        return None

    top = min(band_start, band_end)
    bottom = max(band_start, band_end) + 1
    if bottom - top < max(24, int(page_height * 0.035)):
        return None
    return top, bottom


def crop_horizontal_bounds(
    gray: Image.Image,
    band_top: int,
    band_bottom: int,
    page_width: int,
) -> tuple[int, int] | None:
    col_density = compute_col_density(gray, band_top, band_bottom)
    threshold = 0.01
    active = [i for i, density in enumerate(col_density) if density >= threshold]
    if not active:
        return None
    left = max(0, min(active) - max(8, int(page_width * 0.01)))
    right = min(page_width, max(active) + max(8, int(page_width * 0.01)))
    if right - left < max(40, int(page_width * 0.15)):
        return None
    return left, right


def score_candidate(
    candidate_pdf: tuple[float, float, float, float],
    candidate_px: tuple[int, int, int, int],
    page_rect: fitz.Rect,
    img_size: tuple[int, int],
    label: str,
    direction: str,
    graphic_rects: list[tuple[float, float, float, float]],
    text_rects: list[tuple[float, float, float, float]],
) -> tuple[float, list[str]]:
    reasons: list[str] = []
    page_area = page_rect.width * page_rect.height
    area = max(1.0, (candidate_pdf[2] - candidate_pdf[0]) * (candidate_pdf[3] - candidate_pdf[1]))
    area_ratio = area / max(1.0, page_area)
    score = area_ratio * 6.0
    reasons.append(f"area_ratio={area_ratio:.3f}")

    label_bonus = {
        "figure": 1.4,
        "fig.": 1.4,
        "fig": 1.4,
        "chart": 1.3,
        "table": 1.1,
        "panel": 1.0,
        "exhibit": 0.9,
    }.get(label, 1.0)
    score += label_bonus
    reasons.append(f"label_bonus={label_bonus:.2f}")

    if label in {"figure", "fig", "fig.", "chart", "panel"} and direction == "above":
        score += 0.8
        reasons.append("preferred_above_caption")
    if label == "table" and direction == "below":
        score += 0.4
        reasons.append("table_below_bonus")

    graphic_overlap = sum(rect_intersection_area(candidate_pdf, rect) for rect in graphic_rects)
    if graphic_overlap > 0:
        overlap_ratio = min(1.0, graphic_overlap / area)
        score += 1.2 * overlap_ratio
        reasons.append(f"graphic_overlap={overlap_ratio:.2f}")

    text_overlap = sum(rect_intersection_area(candidate_pdf, rect) for rect in text_rects)
    if text_overlap > 0:
        text_ratio = min(1.0, text_overlap / area)
        score -= 1.0 * text_ratio
        reasons.append(f"text_penalty={text_ratio:.2f}")

    px_w = candidate_px[2] - candidate_px[0]
    px_h = candidate_px[3] - candidate_px[1]
    page_w, page_h = img_size
    if px_w >= int(page_w * 0.5):
        score += 0.5
        reasons.append("wide_region_bonus")
    if px_h >= int(page_h * 0.18):
        score += 0.4
        reasons.append("tall_region_bonus")
    return score, reasons


def build_text_rects(page: fitz.Page, caption_bbox: tuple[float, float, float, float]) -> list[tuple[float, float, float, float]]:
    rects: list[tuple[float, float, float, float]] = []
    text_dict = page.get_text("dict")
    for block in text_dict.get("blocks", []):
        if block.get("type") != 0:
            continue
        bbox = tuple(block.get("bbox", (0, 0, 0, 0)))  # type: ignore[arg-type]
        if rect_intersection_area(bbox, caption_bbox) > 0:
            continue
        rects.append(bbox)
    return rects


def candidate_from_caption(
    page: fitz.Page,
    img: Image.Image,
    gray: Image.Image,
    caption: CaptionBlock,
    graphic_rects: list[tuple[float, float, float, float]],
) -> CandidateRegion | None:
    page_rect = page.rect
    img_w, img_h = img.size
    caption_px = pdf_to_px(page_rect, caption.bbox_pdf, img_w, img_h)
    row_density = compute_row_density(gray)
    text_rects = build_text_rects(page, caption.bbox_pdf)

    regions: list[CandidateRegion] = []
    for direction in ("above", "below"):
        band = find_band(row_density, caption_px[1], caption_px[3], direction, img_h)
        if band is None:
            continue
        bounds = crop_horizontal_bounds(gray, band[0], band[1], img_w)
        if bounds is None:
            continue
        bbox_px = (bounds[0], band[0], bounds[1], band[1])
        bbox_pdf = px_to_pdf(page_rect, bbox_px, img_w, img_h)
        score, reasons = score_candidate(
            bbox_pdf,
            bbox_px,
            page_rect,
            (img_w, img_h),
            caption.label,
            direction,
            graphic_rects,
            text_rects,
        )
        regions.append(
            CandidateRegion(
                page_index=caption.page_index,
                page_number=caption.page_number,
                caption_label=caption.label,
                caption_key=caption.key,
                caption_text=caption.text,
                direction=direction,
                bbox_pdf=bbox_pdf,
                bbox_px=bbox_px,
                score=score,
                reason=reasons,
            )
        )

    if not regions:
        return None
    regions.sort(key=lambda item: item.score, reverse=True)
    return regions[0]


def dedupe_regions(candidates: Iterable[CandidateRegion]) -> list[CandidateRegion]:
    best_by_caption: dict[tuple[int, str], CandidateRegion] = {}
    for candidate in candidates:
        key = (candidate.page_index, candidate.caption_key)
        current = best_by_caption.get(key)
        if current is None or candidate.score > current.score:
            best_by_caption[key] = candidate

    chosen: list[CandidateRegion] = []
    for candidate in sorted(best_by_caption.values(), key=lambda item: item.score, reverse=True):
        overlapped = False
        for existing in chosen:
            overlap = rect_intersection_area(candidate.bbox_pdf, existing.bbox_pdf)
            area = max(
                1.0,
                (candidate.bbox_pdf[2] - candidate.bbox_pdf[0]) * (candidate.bbox_pdf[3] - candidate.bbox_pdf[1]),
            )
            if candidate.page_index == existing.page_index and overlap / area > 0.65:
                overlapped = True
                break
        if not overlapped:
            chosen.append(candidate)
    return chosen


def fallback_image_blocks(
    page: fitz.Page,
    img: Image.Image,
    graphic_rects: list[tuple[float, float, float, float]],
) -> list[CandidateRegion]:
    page_rect = page.rect
    img_w, img_h = img.size
    page_area = page_rect.width * page_rect.height
    candidates: list[CandidateRegion] = []
    for idx, rect in enumerate(graphic_rects, start=1):
        area = max(1.0, (rect[2] - rect[0]) * (rect[3] - rect[1]))
        if area / max(1.0, page_area) < 0.04:
            continue
        bbox_px = pdf_to_px(page_rect, rect, img_w, img_h)
        score = (area / page_area) * 6.0 + 0.4
        candidates.append(
            CandidateRegion(
                page_index=page.number,
                page_number=page.number + 1,
                caption_label="graphic",
                caption_key=f"graphic-{idx}",
                caption_text=f"graphic-block-{idx}",
                direction="fallback",
                bbox_pdf=rect,
                bbox_px=bbox_px,
                score=score,
                reason=["fallback_graphic_block"],
            )
        )
    return candidates


def save_crop(
    img: Image.Image,
    candidate: CandidateRegion,
    out_dir: Path,
    rank: int,
    save_page_previews: bool,
) -> dict[str, object]:
    crop = img.crop(candidate.bbox_px)
    label_slug = re.sub(r"[^a-z0-9]+", "-", candidate.caption_label.lower()).strip("-") or "figure"
    out_name = f"rank-{rank:02d}-page-{candidate.page_number:03d}-{label_slug}.png"
    out_path = out_dir / out_name
    crop.save(out_path)

    preview_rel = None
    if save_page_previews:
        preview_name = f"page-{candidate.page_number:03d}.png"
        preview_path = out_dir / preview_name
        if not preview_path.exists():
            img.save(preview_path)
        preview_rel = preview_name

    return {
        "rank": rank,
        "page_number": candidate.page_number,
        "caption_label": candidate.caption_label,
        "caption_key": candidate.caption_key,
        "caption_text": candidate.caption_text,
        "what_it_shows": summarize_visual(candidate),
        "direction": candidate.direction,
        "score": round(candidate.score, 4),
        "bbox_pdf": [round(value, 2) for value in candidate.bbox_pdf],
        "bbox_px": list(candidate.bbox_px),
        "crop_path": out_name,
        "page_preview_path": preview_rel,
        "reason": candidate.reason,
    }


def main() -> int:
    args = parse_args()
    pdf_path = Path(args.pdf).expanduser().resolve()
    if not pdf_path.exists():
        print(f"PDF not found: {pdf_path}", file=sys.stderr)
        return 1

    out_dir = (
        Path(args.out_dir).expanduser().resolve()
        if args.out_dir
        else pdf_path.with_suffix("")
        .with_name(f"{pdf_path.stem}_figures")
        .resolve()
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf_path)
    page_limit = doc.page_count if args.max_pages <= 0 else min(args.max_pages, doc.page_count)

    all_candidates: list[CandidateRegion] = []
    page_images: dict[int, Image.Image] = {}
    for page_index in range(page_limit):
        page = doc[page_index]
        img, gray = render_page(page, args.dpi)
        page_images[page_index] = img
        captions = collect_captions(page, page_index)
        graphic_rects = collect_graphic_rects(page)
        if captions:
            for caption in captions:
                candidate = candidate_from_caption(page, img, gray, caption, graphic_rects)
                if candidate is not None:
                    all_candidates.append(candidate)
        else:
            all_candidates.extend(fallback_image_blocks(page, img, graphic_rects))

    ranked = dedupe_regions(all_candidates)[: max(1, args.top_k)]
    exports: list[dict[str, object]] = []
    for rank, candidate in enumerate(ranked, start=1):
        exports.append(
            save_crop(
                page_images[candidate.page_index],
                candidate,
                out_dir,
                rank,
                args.save_page_previews,
            )
        )

    summary = {
        "pdf": str(pdf_path),
        "out_dir": str(out_dir),
        "page_count_scanned": page_limit,
        "candidates_found": len(all_candidates),
        "exports": exports,
    }

    summary_path = Path(args.summary_json).expanduser().resolve() if args.summary_json else out_dir / "manifest.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
