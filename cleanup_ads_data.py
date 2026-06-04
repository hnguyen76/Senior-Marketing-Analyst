from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from typing import Any


"""
Goal:
1. Load three paid-media exports from Facebook, Google, and TikTok.
2. Standardize their different column names into one common schema.
3. Clean numeric fields and recompute performance metrics from raw counts.
4. Merge duplicate rows at the same date/platform/campaign/ad-group grain.
5. Export a clean unified table and a channel-level summary.

"""


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"

SOURCE_FILES = [
    {
        "platform": "Facebook",
        "path": DATA_DIR / "01_facebook_ads.csv",
        "spend_col": "spend",
        "ad_group_id_col": "ad_set_id",
        "ad_group_name_col": "ad_set_name",
    },
    {
        "platform": "Google",
        "path": DATA_DIR / "02_google_ads.csv",
        "spend_col": "cost",
        "ad_group_id_col": "ad_group_id",
        "ad_group_name_col": "ad_group_name",
    },
    {
        "platform": "TikTok",
        "path": DATA_DIR / "03_tiktok_ads.csv",
        "spend_col": "cost",
        "ad_group_id_col": "adgroup_id",
        "ad_group_name_col": "adgroup_name",
    },
]

UNIFIED_COLUMNS = [
    "date",
    "platform",
    "campaign_id",
    "campaign_name",
    "objective",
    "ad_group_id",
    "ad_group_name",
    "impressions",
    "clicks",
    "spend",
    "conversions",
    "conversion_value",
    "video_views",
    "video_watch_25",
    "video_watch_50",
    "video_watch_75",
    "video_watch_100",
    "likes",
    "shares",
    "comments",
    "reach",
    "frequency",
    "quality_score",
    "search_impression_share",
    "engagements",
    "engagement_rate",
    "ctr",
    "cpc",
    "cpm",
    "cvr",
    "cpa",
    "roas",
    "video_view_rate",
    "video_completion_rate",
    "source_file",
]

SUMMARY_COLUMNS = [
    "platform",
    "impressions",
    "clicks",
    "spend",
    "conversions",
    "conversion_value",
    "ctr",
    "cpc",
    "cpm",
    "cvr",
    "cpa",
    "roas",
    "video_views",
    "video_completion_rate",
]

ADDITIVE_FIELDS = [
    "impressions",
    "clicks",
    "spend",
    "conversions",
    "conversion_value",
    "video_views",
    "video_watch_25",
    "video_watch_50",
    "video_watch_75",
    "video_watch_100",
    "likes",
    "shares",
    "comments",
    "reach",
    "engagements",
]

AVERAGE_FIELDS = ["frequency", "quality_score", "search_impression_share"]


def to_number(value: Any) -> float | None:
    """Convert source values to clean non-negative numbers."""
    if value is None:
        return None

    text = str(value).strip()
    if text == "":
        return None

    try:
        number = float(text.replace(",", ""))
    except ValueError:
        return None

    return max(number, 0.0)


def divide(numerator: float | None, denominator: float | None) -> float | None:
    """Return a safe ratio, keeping blanks instead of divide-by-zero errors."""
    if numerator is None or denominator in (None, 0):
        return None
    return numerator / denominator


def infer_objective(campaign_name: str) -> str:
    """Create a readable campaign objective label from campaign naming."""
    name = campaign_name.lower()
    if "retarget" in name or "remarketing" in name:
        return "Retargeting"
    if "shopping" in name:
        return "Shopping"
    if "search" in name or "terms" in name or "generic" in name:
        return "Search"
    if "conversion" in name:
        return "Conversion"
    if "traffic" in name:
        return "Traffic"
    if "influencer" in name:
        return "Influencer"
    if "brand" in name or "awareness" in name or "video" in name:
        return "Awareness"
    return "Other"


def add_calculated_metrics(row: dict[str, Any]) -> dict[str, Any]:
    """Recompute KPIs from raw counts so every platform uses the same formulas."""
    impressions = row.get("impressions") or 0.0
    clicks = row.get("clicks") or 0.0
    spend = row.get("spend") or 0.0
    conversions = row.get("conversions") or 0.0
    conversion_value = row.get("conversion_value")
    video_views = row.get("video_views")
    video_complete = row.get("video_watch_100")
    engagements = row.get("engagements")

    row["ctr"] = divide(clicks, impressions)
    row["cpc"] = divide(spend, clicks)
    row["cpm"] = divide(spend * 1000, impressions)
    row["cvr"] = divide(conversions, clicks)
    row["cpa"] = divide(spend, conversions)
    row["roas"] = divide(conversion_value, spend) if conversion_value else None
    row["video_view_rate"] = divide(video_views, impressions) if video_views else None
    row["video_completion_rate"] = divide(video_complete, video_views) if video_views else None

    if row.get("engagement_rate") is None:
        row["engagement_rate"] = divide(engagements, impressions) if engagements else None

    return row


def normalize_source_row(raw: dict[str, str], source: dict[str, Any]) -> dict[str, Any] | None:
    """Map each platform export into the unified schema."""
    date = raw.get("date", "").strip()
    campaign_id = raw.get("campaign_id", "").strip()
    campaign_name = raw.get("campaign_name", "").strip()
    ad_group_id = raw.get(source["ad_group_id_col"], "").strip()
    ad_group_name = raw.get(source["ad_group_name_col"], "").strip()

    if not all([date, campaign_id, campaign_name, ad_group_id]):
        return None

    platform = source["platform"]
    likes = to_number(raw.get("likes")) or 0.0
    shares = to_number(raw.get("shares")) or 0.0
    comments = to_number(raw.get("comments")) or 0.0

    row = {
        "date": date,
        "platform": platform,
        "campaign_id": campaign_id,
        "campaign_name": campaign_name,
        "objective": infer_objective(campaign_name),
        "ad_group_id": ad_group_id,
        "ad_group_name": ad_group_name,
        "impressions": to_number(raw.get("impressions")) or 0.0,
        "clicks": to_number(raw.get("clicks")) or 0.0,
        "spend": to_number(raw.get(source["spend_col"])) or 0.0,
        "conversions": to_number(raw.get("conversions")) or 0.0,
        "conversion_value": to_number(raw.get("conversion_value")),
        "video_views": to_number(raw.get("video_views")),
        "video_watch_25": to_number(raw.get("video_watch_25")),
        "video_watch_50": to_number(raw.get("video_watch_50")),
        "video_watch_75": to_number(raw.get("video_watch_75")),
        "video_watch_100": to_number(raw.get("video_watch_100")),
        "likes": likes if platform == "TikTok" else None,
        "shares": shares if platform == "TikTok" else None,
        "comments": comments if platform == "TikTok" else None,
        "reach": to_number(raw.get("reach")),
        "frequency": to_number(raw.get("frequency")),
        "quality_score": to_number(raw.get("quality_score")),
        "search_impression_share": to_number(raw.get("search_impression_share")),
        "engagements": likes + shares + comments if platform == "TikTok" else None,
        "engagement_rate": to_number(raw.get("engagement_rate")),
        "source_file": source["path"].name,
    }

    return add_calculated_metrics(row)


def merge_duplicate_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Merge rows at the final reporting grain: date/platform/campaign/ad group."""
    merged: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    average_counts: dict[tuple[str, str, str, str], dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for row in rows:
        key = (row["date"], row["platform"], row["campaign_id"], row["ad_group_id"])

        if key not in merged:
            merged[key] = {column: row.get(column) for column in UNIFIED_COLUMNS}
            for field in AVERAGE_FIELDS:
                if row.get(field) is not None:
                    average_counts[key][field] = 1
            continue

        target = merged[key]
        for field in ADDITIVE_FIELDS:
            if row.get(field) is None and target.get(field) is None:
                continue
            target[field] = (target.get(field) or 0.0) + (row.get(field) or 0.0)

        for field in AVERAGE_FIELDS:
            if row.get(field) is not None:
                target[field] = (target.get(field) or 0.0) + row[field]
                average_counts[key][field] += 1

    for key, row in merged.items():
        for field in AVERAGE_FIELDS:
            count = average_counts[key][field]
            row[field] = row[field] / count if count else None
        add_calculated_metrics(row)

    return sorted(
        merged.values(),
        key=lambda item: (item["date"], item["platform"], item["campaign_id"], item["ad_group_id"]),
    )


def load_and_clean_data() -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Load all source files, normalize rows, and track cleanup counts."""
    raw_rows = 0
    invalid_rows = 0
    normalized_rows: list[dict[str, Any]] = []

    for source in SOURCE_FILES:
        with source["path"].open(newline="", encoding="utf-8-sig") as handle:
            for raw in csv.DictReader(handle):
                raw_rows += 1
                normalized = normalize_source_row(raw, source)
                if normalized is None:
                    invalid_rows += 1
                    continue
                normalized_rows.append(normalized)

    clean_rows = merge_duplicate_rows(normalized_rows)
    return clean_rows, {
        "raw_rows": raw_rows,
        "clean_rows": len(clean_rows),
        "invalid_rows_dropped": invalid_rows,
        "duplicates_merged": len(normalized_rows) - len(clean_rows),
    }


def summarize_by_platform(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Create the executive summary table used for quick business review."""
    summary: dict[str, dict[str, Any]] = {}
    field_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for row in rows:
        platform = row["platform"]
        if platform not in summary:
            summary[platform] = {field: 0.0 for field in ADDITIVE_FIELDS}
            summary[platform]["platform"] = platform

        for field in ADDITIVE_FIELDS:
            if row.get(field) is not None:
                summary[platform][field] += row[field]
                field_counts[platform][field] += 1

    output = []
    for platform, row in summary.items():
        for field in ADDITIVE_FIELDS:
            if field_counts[platform][field] == 0:
                row[field] = None
        add_calculated_metrics(row)
        output.append(row)

    return sorted(output, key=lambda item: item["spend"], reverse=True)


def format_csv_value(field: str, value: Any) -> str:
    """Keep exported CSV values readable and consistently rounded."""
    if value is None:
        return ""

    text_fields = {
        "date",
        "platform",
        "campaign_id",
        "campaign_name",
        "objective",
        "ad_group_id",
        "ad_group_name",
        "source_file",
    }
    integer_fields = {
        "impressions",
        "clicks",
        "conversions",
        "video_views",
        "video_watch_25",
        "video_watch_50",
        "video_watch_75",
        "video_watch_100",
        "likes",
        "shares",
        "comments",
        "reach",
        "engagements",
    }
    money_fields = {"spend", "conversion_value", "cpc", "cpm", "cpa"}

    if field in text_fields:
        return str(value)
    if field in integer_fields:
        return str(int(round(float(value))))
    if field in money_fields:
        return f"{float(value):.2f}"
    return f"{float(value):.4f}"


def write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: format_csv_value(field, row.get(field)) for field in columns})


def print_summary(cleanup_stats: dict[str, int], summary_rows: list[dict[str, Any]]) -> None:
    total_spend = sum(row["spend"] for row in summary_rows)
    total_conversions = sum(row["conversions"] for row in summary_rows)
    blended_cpa = divide(total_spend, total_conversions)

    print("\nPaid Media Cleanup Summary")
    print("-" * 31)
    print(f"Source rows loaded:       {cleanup_stats['raw_rows']:,}")
    print(f"Clean rows exported:      {cleanup_stats['clean_rows']:,}")
    print(f"Invalid rows dropped:     {cleanup_stats['invalid_rows_dropped']:,}")
    print(f"Duplicate rows merged:    {cleanup_stats['duplicates_merged']:,}")
    print(f"Total spend:              ${total_spend:,.2f}")
    print(f"Total conversions:        {total_conversions:,.0f}")
    print(f"Blended CPA:              ${blended_cpa:,.2f}")
    print("\nChannel Performance")
    print(f"{'Platform':<12}{'Spend':>14}{'Conversions':>14}{'CPA':>11}{'CTR':>10}{'ROAS':>10}")

    for row in summary_rows:
        roas = f"{row['roas']:.2f}x" if row.get("roas") else "n/a"
        print(
            f"{row['platform']:<12}"
            f"{'$' + format(row['spend'], ',.2f'):>14}"
            f"{row['conversions']:>14,.0f}"
            f"{'$' + format(row['cpa'], ',.2f'):>11}"
            f"{format(row['ctr'] * 100, '.2f') + '%':>10}"
            f"{roas:>9}"
        )


def main() -> None:
    clean_rows, cleanup_stats = load_and_clean_data()
    summary_rows = summarize_by_platform(clean_rows)

    clean_output = DATA_DIR / "unified_ads_clean.csv"
    summary_output = DATA_DIR / "channel_summary.csv"

    write_csv(clean_output, clean_rows, UNIFIED_COLUMNS)
    write_csv(summary_output, summary_rows, SUMMARY_COLUMNS)
    print_summary(cleanup_stats, summary_rows)

    print("\nFiles created")
    print(f"- {clean_output.relative_to(ROOT)}")
    print(f"- {summary_output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
