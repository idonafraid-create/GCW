#!/usr/bin/env python3
"""Compare every GCW source/candidate screenshot pair and emit reports."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageEnhance


def percentile(histogram: list[int], value: float) -> int:
    target = sum(histogram) * value
    seen = 0
    for index, count in enumerate(histogram):
        seen += count
        if seen >= target:
            return index
    return len(histogram) - 1


def compare(source_path: Path, candidate_path: Path, threshold: int, diff_path: Path) -> dict:
    source = Image.open(source_path).convert("RGB")
    candidate = Image.open(candidate_path).convert("RGB")
    if source.size != candidate.size:
        return {"status": "failed", "error": f"image sizes differ: {source.size} vs {candidate.size}"}

    diff = ImageChops.difference(source, candidate)
    pixels = source.width * source.height
    pixel_data = diff.get_flattened_data() if hasattr(diff, "get_flattened_data") else diff.getdata()
    changed = sum(1 for rgb in pixel_data if max(rgb) > threshold)
    histogram = diff.histogram()
    combined = [histogram[i] + histogram[256 + i] + histogram[512 + i] for i in range(256)]
    mean_abs = sum(index * count for index, count in enumerate(combined)) / (pixels * 3)
    diff_path.parent.mkdir(parents=True, exist_ok=True)
    ImageEnhance.Contrast(diff).enhance(4).save(diff_path)
    return {
        "status": "measured",
        "width": source.width,
        "height": source.height,
        "threshold": threshold,
        "meanAbs": round(mean_abs, 6),
        "changedPct": round(changed * 100 / pixels, 6),
        "p95ChannelDifference": percentile(combined, 0.95),
        "maxChannelDifference": max((i for i, count in enumerate(combined) if count), default=0),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("results_dir", type=Path)
    parser.add_argument("--diff-dir", type=Path)
    parser.add_argument("--threshold", type=int, default=4)
    parser.add_argument("--max-changed-pct", type=float, default=1.0)
    parser.add_argument("--max-mean-abs", type=float, default=2.0)
    parser.add_argument("--report-json", type=Path)
    parser.add_argument("--report-md", type=Path)
    args = parser.parse_args()

    root = args.results_dir.resolve()
    diff_dir = (args.diff_dir or root / "diff").resolve()
    report_json = (args.report_json or root / "visual-diff-report.json").resolve()
    report_md = (args.report_md or root / "visual-diff-report.md").resolve()
    pairs = []
    failed = False

    for source_path in sorted(root.glob("*.source.png")):
        scenario = source_path.name.removesuffix(".source.png")
        candidate_path = root / f"{scenario}.candidate.png"
        if not candidate_path.exists():
            pairs.append({"scenario": scenario, "status": "failed", "error": "candidate image missing"})
            failed = True
            continue
        metrics = compare(source_path, candidate_path, args.threshold, diff_dir / f"{scenario}.diff.png")
        passed = (
            metrics.get("status") == "measured"
            and metrics["changedPct"] <= args.max_changed_pct
            and metrics["meanAbs"] <= args.max_mean_abs
        )
        metrics.update({
            "scenario": scenario,
            "source": source_path.name,
            "candidate": candidate_path.name,
            "diff": str((diff_dir / f"{scenario}.diff.png").relative_to(root)) if diff_dir.is_relative_to(root) else str(diff_dir / f"{scenario}.diff.png"),
            "passed": passed,
        })
        pairs.append(metrics)
        failed = failed or not passed

    if not pairs:
        parser.error(f"no *.source.png files found in {root}")

    report = {
        "schemaVersion": 1,
        "thresholds": {
            "pixelChannel": args.threshold,
            "maxChangedPct": args.max_changed_pct,
            "maxMeanAbs": args.max_mean_abs,
        },
        "passed": not failed,
        "scenarios": pairs,
    }
    report_json.parent.mkdir(parents=True, exist_ok=True)
    report_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# GCW visual diff report",
        "",
        f"Overall: **{'PASS' if not failed else 'FAIL'}**",
        "",
        "| Scenario | Changed > threshold | Mean abs | P95 | Result |",
        "|---|---:|---:|---:|---|",
    ]
    for item in pairs:
        if item.get("status") == "measured":
            lines.append(f"| {item['scenario']} | {item['changedPct']:.6f}% | {item['meanAbs']:.6f} | {item['p95ChannelDifference']} | {'PASS' if item['passed'] else 'FAIL'} |")
        else:
            lines.append(f"| {item['scenario']} | — | — | — | FAIL: {item.get('error', 'unknown')} |")
    report_md.parent.mkdir(parents=True, exist_ok=True)
    report_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"passed": not failed, "json": str(report_json), "markdown": str(report_md)}, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

