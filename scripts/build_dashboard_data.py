from __future__ import annotations

import csv
import json
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ASSETS_DIR = ROOT / "assets"

SOURCE_CONFIGS = [
    {
        "platform": "Facebook",
        "file": DATA_DIR / "01_facebook_ads.csv",
        "spend_col": "spend",
        "ad_group_id_col": "ad_set_id",
        "ad_group_name_col": "ad_set_name",
    },
    {
        "platform": "Google",
        "file": DATA_DIR / "02_google_ads.csv",
        "spend_col": "cost",
        "ad_group_id_col": "ad_group_id",
        "ad_group_name_col": "ad_group_name",
    },
    {
        "platform": "TikTok",
        "file": DATA_DIR / "03_tiktok_ads.csv",
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

ADDITIVE_COLUMNS = [
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

AVERAGE_COLUMNS = ["frequency", "quality_score", "search_impression_share"]


def as_float(value: Any) -> float | None:
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


def safe_div(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return numerator / denominator


def detect_objective(campaign_name: str) -> str:
    name = campaign_name.lower()
    if "retarget" in name or "remarketing" in name:
        return "Retargeting"
    if "shopping" in name:
        return "Shopping"
    if "generic" in name or "search" in name or "terms" in name:
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


def metric_row(row: dict[str, Any]) -> dict[str, Any]:
    impressions = row.get("impressions") or 0.0
    clicks = row.get("clicks") or 0.0
    spend = row.get("spend") or 0.0
    conversions = row.get("conversions") or 0.0
    conversion_value = row.get("conversion_value")
    video_views = row.get("video_views")
    video_watch_100 = row.get("video_watch_100")
    engagements = row.get("engagements")

    row["ctr"] = safe_div(clicks, impressions)
    row["cpc"] = safe_div(spend, clicks)
    row["cpm"] = safe_div(spend * 1000, impressions)
    row["cvr"] = safe_div(conversions, clicks)
    row["cpa"] = safe_div(spend, conversions)
    row["roas"] = safe_div(conversion_value, spend) if conversion_value else None
    row["video_view_rate"] = safe_div(video_views, impressions) if video_views else None
    row["video_completion_rate"] = safe_div(video_watch_100, video_views) if video_views else None
    if row.get("engagement_rate") is None:
        row["engagement_rate"] = safe_div(engagements, impressions) if engagements else None
    return row


def normalize_row(row: dict[str, str], config: dict[str, Any]) -> dict[str, Any] | None:
    date = row.get("date", "").strip()
    campaign_id = row.get("campaign_id", "").strip()
    campaign_name = row.get("campaign_name", "").strip()
    ad_group_id = row.get(config["ad_group_id_col"], "").strip()
    ad_group_name = row.get(config["ad_group_name_col"], "").strip()
    if not (date and campaign_id and campaign_name and ad_group_id):
        return None

    platform = config["platform"]
    spend = as_float(row.get(config["spend_col"])) or 0.0
    impressions = as_float(row.get("impressions")) or 0.0
    clicks = as_float(row.get("clicks")) or 0.0
    conversions = as_float(row.get("conversions")) or 0.0
    likes = as_float(row.get("likes")) or 0.0
    shares = as_float(row.get("shares")) or 0.0
    comments = as_float(row.get("comments")) or 0.0
    engagements = likes + shares + comments if platform == "TikTok" else None

    normalized = {
        "date": date,
        "platform": platform,
        "campaign_id": campaign_id,
        "campaign_name": campaign_name,
        "objective": detect_objective(campaign_name),
        "ad_group_id": ad_group_id,
        "ad_group_name": ad_group_name,
        "impressions": impressions,
        "clicks": clicks,
        "spend": spend,
        "conversions": conversions,
        "conversion_value": as_float(row.get("conversion_value")),
        "video_views": as_float(row.get("video_views")),
        "video_watch_25": as_float(row.get("video_watch_25")),
        "video_watch_50": as_float(row.get("video_watch_50")),
        "video_watch_75": as_float(row.get("video_watch_75")),
        "video_watch_100": as_float(row.get("video_watch_100")),
        "likes": likes if platform == "TikTok" else None,
        "shares": shares if platform == "TikTok" else None,
        "comments": comments if platform == "TikTok" else None,
        "reach": as_float(row.get("reach")),
        "frequency": as_float(row.get("frequency")),
        "quality_score": as_float(row.get("quality_score")),
        "search_impression_share": as_float(row.get("search_impression_share")),
        "engagements": engagements,
        "engagement_rate": as_float(row.get("engagement_rate")),
        "source_file": config["file"].name,
    }
    return metric_row(normalized)


def load_clean_rows() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    raw_count = 0
    missing_required = 0
    normalized_rows: list[dict[str, Any]] = []

    for config in SOURCE_CONFIGS:
        with config["file"].open(newline="", encoding="utf-8-sig") as handle:
            for source_row in csv.DictReader(handle):
                raw_count += 1
                row = normalize_row(source_row, config)
                if row is None:
                    missing_required += 1
                    continue
                normalized_rows.append(row)

    grouped: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    average_counts: dict[tuple[str, str, str, str], dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for row in normalized_rows:
        key = (row["date"], row["platform"], row["campaign_id"], row["ad_group_id"])
        if key not in grouped:
            grouped[key] = {column: row.get(column) for column in UNIFIED_COLUMNS}
            for average_col in AVERAGE_COLUMNS:
                if grouped[key].get(average_col) is not None:
                    average_counts[key][average_col] = 1
            continue

        target = grouped[key]
        for column in ADDITIVE_COLUMNS:
            if row.get(column) is None and target.get(column) is None:
                continue
            target[column] = (target.get(column) or 0.0) + (row.get(column) or 0.0)
        for average_col in AVERAGE_COLUMNS:
            if row.get(average_col) is not None:
                target[average_col] = (target.get(average_col) or 0.0) + row[average_col]
                average_counts[key][average_col] += 1
        target["source_file"] = f'{target["source_file"]};{row["source_file"]}'

    for key, row in grouped.items():
        for average_col in AVERAGE_COLUMNS:
            count = average_counts[key][average_col]
            if count:
                row[average_col] = row[average_col] / count
        metric_row(row)

    clean_rows = sorted(
        grouped.values(),
        key=lambda item: (item["date"], item["platform"], item["campaign_id"], item["ad_group_id"]),
    )
    quality = {
        "raw_rows": raw_count,
        "clean_rows": len(clean_rows),
        "duplicates_merged": len(normalized_rows) - len(clean_rows),
        "missing_required_rows_dropped": missing_required,
        "source_files": [config["file"].name for config in SOURCE_CONFIGS],
    }
    return clean_rows, quality


def round_or_none(value: Any, digits: int = 4) -> float | None:
    if value is None:
        return None
    return round(float(value), digits)


def csv_value(column: str, value: Any) -> str:
    if value is None:
        return ""
    if column in {"date", "platform", "campaign_id", "campaign_name", "objective", "ad_group_id", "ad_group_name", "source_file"}:
        return str(value)
    if column in {"impressions", "clicks", "conversions", "video_views", "video_watch_25", "video_watch_50", "video_watch_75", "video_watch_100", "likes", "shares", "comments", "reach", "engagements"}:
        return str(int(round(float(value))))
    if column in {"spend", "conversion_value", "cpc", "cpm", "cpa"}:
        return f"{float(value):.2f}"
    return f"{float(value):.4f}"


def rollup(rows: list[dict[str, Any]], group_by: list[str]) -> list[dict[str, Any]]:
    groups: dict[tuple[Any, ...], dict[str, Any]] = {}
    frequency_count: dict[tuple[Any, ...], int] = defaultdict(int)
    quality_score_count: dict[tuple[Any, ...], int] = defaultdict(int)
    search_share_count: dict[tuple[Any, ...], int] = defaultdict(int)

    for row in rows:
        key = tuple(row[field] for field in group_by)
        if key not in groups:
            groups[key] = {field: row[field] for field in group_by}
            for column in ADDITIVE_COLUMNS:
                groups[key][column] = 0.0
            groups[key]["frequency"] = 0.0
            groups[key]["quality_score"] = 0.0
            groups[key]["search_impression_share"] = 0.0

        target = groups[key]
        for column in ADDITIVE_COLUMNS:
            target[column] += row.get(column) or 0.0
        if row.get("frequency") is not None:
            target["frequency"] += row["frequency"]
            frequency_count[key] += 1
        if row.get("quality_score") is not None:
            target["quality_score"] += row["quality_score"]
            quality_score_count[key] += 1
        if row.get("search_impression_share") is not None:
            target["search_impression_share"] += row["search_impression_share"]
            search_share_count[key] += 1

    summary: list[dict[str, Any]] = []
    for key, target in groups.items():
        if frequency_count[key]:
            target["frequency"] = target["frequency"] / frequency_count[key]
        else:
            target["frequency"] = None
        if quality_score_count[key]:
            target["quality_score"] = target["quality_score"] / quality_score_count[key]
        else:
            target["quality_score"] = None
        if search_share_count[key]:
            target["search_impression_share"] = target["search_impression_share"] / search_share_count[key]
        else:
            target["search_impression_share"] = None
        metric_row(target)
        summary.append(target)
    return summary


def output_metric(row: dict[str, Any]) -> dict[str, Any]:
    keys = [
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
    output: dict[str, Any] = {}
    for key, value in row.items():
        if key in keys:
            output[key] = round_or_none(value, 2)
        elif key in {"frequency", "quality_score", "search_impression_share", "engagement_rate", "ctr", "cpc", "cpm", "cvr", "cpa", "roas", "video_view_rate", "video_completion_rate"}:
            output[key] = round_or_none(value, 5)
        else:
            output[key] = value
    return output


def make_insights(platforms: list[dict[str, Any]], campaigns: list[dict[str, Any]]) -> list[dict[str, str]]:
    cpa_platforms = [platform for platform in platforms if platform.get("cpa")]
    best_cpa_platform = min(cpa_platforms, key=lambda item: item["cpa"])
    highest_roas_campaign = max(
        [campaign for campaign in campaigns if campaign.get("roas")],
        key=lambda item: item["roas"],
    )
    highest_cvr_campaign = max(
        [campaign for campaign in campaigns if campaign.get("clicks") and campaign.get("conversions")],
        key=lambda item: item["cvr"],
    )
    largest_spend_platform = max(platforms, key=lambda item: item["spend"])
    highest_cpa_campaign = max(
        [campaign for campaign in campaigns if campaign.get("cpa")],
        key=lambda item: item["cpa"],
    )

    return [
        {
            "label": "Protect profitable demand",
            "text": (
                f"{highest_roas_campaign['campaign_name']} delivers the strongest tracked ROAS at "
                f"{highest_roas_campaign['roas']:.2f}x with a ${highest_roas_campaign['cpa']:.2f} CPA. "
                "Keep brand/search and shopping coverage high before funding lower-intent volume."
            ),
        },
        {
            "label": "Scale efficient conversion audiences",
            "text": (
                f"{best_cpa_platform['platform']} has the lowest blended CPA at "
                f"${best_cpa_platform['cpa']:.2f}. Use it as the benchmark for incremental budget tests."
            ),
        },
        {
            "label": "Retargeting converts best",
            "text": (
                f"{highest_cvr_campaign['campaign_name']} posts the best click-to-conversion rate at "
                f"{highest_cvr_campaign['cvr'] * 100:.1f}%. Expand audience freshness rules and creative variants here."
            ),
        },
        {
            "label": "TikTok is a reach engine",
            "text": (
                f"{largest_spend_platform['platform']} carries the largest spend share and top impression scale. "
                "Use it to build engaged pools, then retarget the highest-intent viewers in conversion channels."
            ),
        },
        {
            "label": "Trim weak efficiency",
            "text": (
                f"{highest_cpa_campaign['campaign_name']} has the highest CPA at "
                f"${highest_cpa_campaign['cpa']:.2f}. Reduce bids or isolate only the highest-converting segments."
            ),
        },
    ]


def build_dashboard_data(clean_rows: list[dict[str, Any]], quality: dict[str, Any]) -> dict[str, Any]:
    totals = output_metric(rollup(clean_rows, [])[0])
    platform_metrics = sorted(rollup(clean_rows, ["platform"]), key=lambda row: row["spend"], reverse=True)
    campaign_metrics = sorted(
        rollup(clean_rows, ["platform", "campaign_id", "campaign_name", "objective"]),
        key=lambda row: row["conversions"],
        reverse=True,
    )
    objective_metrics = sorted(rollup(clean_rows, ["objective"]), key=lambda row: row["spend"], reverse=True)
    daily_totals = sorted(rollup(clean_rows, ["date"]), key=lambda row: row["date"])
    daily_platform = sorted(rollup(clean_rows, ["date", "platform"]), key=lambda row: (row["date"], row["platform"]))

    date_values = sorted({row["date"] for row in clean_rows})
    quality["date_range"] = {
        "start": date_values[0],
        "end": date_values[-1],
        "days": len(date_values),
    }

    return {
        "generated_at": date.today().isoformat(),
        "source": output_metric(quality),
        "totals": totals,
        "platforms": [output_metric(row) for row in platform_metrics],
        "campaigns": [output_metric(row) for row in campaign_metrics],
        "objectives": [output_metric(row) for row in objective_metrics],
        "daily": [output_metric(row) for row in daily_totals],
        "daily_platform": [output_metric(row) for row in daily_platform],
        "insights": make_insights(platform_metrics, campaign_metrics),
    }


def main() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    clean_rows, quality = load_clean_rows()

    unified_csv = DATA_DIR / "unified_ads_clean.csv"
    with unified_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=UNIFIED_COLUMNS)
        writer.writeheader()
        for row in clean_rows:
            writer.writerow({column: csv_value(column, row.get(column)) for column in UNIFIED_COLUMNS})

    dashboard_data = build_dashboard_data(clean_rows, quality)
    dashboard_js = ASSETS_DIR / "dashboard-data.js"
    dashboard_js.write_text(
        "window.DASHBOARD_DATA = "
        + json.dumps(dashboard_data, indent=2, sort_keys=True)
        + ";\n",
        encoding="utf-8",
    )

    print(f"Wrote {unified_csv.relative_to(ROOT)} ({len(clean_rows)} rows)")
    print(f"Wrote {dashboard_js.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
