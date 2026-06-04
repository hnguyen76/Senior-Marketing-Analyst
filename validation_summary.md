# Validation and QA Summary

This summary documents the quality checks used after merging the Facebook, Google, and TikTok source exports.

## Reconciliation

| Check | Result |
|---|---:|
| Source rows loaded | 330 |
| Clean unified rows exported | 330 |
| Invalid rows dropped | 0 |
| Duplicate rows merged | 0 |
| Reporting start date | 2024-01-01 |
| Reporting end date | 2024-01-30 |
| Reporting days | 30 |

## Source Row Counts

| Source file | Platform | Rows |
|---|---|---:|
| `data/01_facebook_ads.csv` | Facebook | 110 |
| `data/02_google_ads.csv` | Google | 110 |
| `data/03_tiktok_ads.csv` | TikTok | 110 |

## Platform Summary

| Platform | Spend | Conversions | CPA | CTR | ROAS |
|---|---:|---:|---:|---:|---:|
| TikTok | $74,266.70 | 6,750 | $11.00 | 1.61% | n/a |
| Google | $37,686.20 | 4,218 | $8.93 | 1.90% | 5.60x |
| Facebook | $18,292.00 | 2,395 | $7.64 | 1.96% | n/a |

## Data Quality Checks

- Confirmed all 330 source rows were included in the unified output.
- Confirmed no required reporting fields were missing after cleanup.
- Confirmed no negative values exist in core numeric fields.
- Recalculated CTR, CPC, CPM, CVR, CPA, and ROAS from raw values instead of relying on source-provided platform rates.
- Preserved platform-specific fields instead of forcing zeros where a platform does not track a metric.
- Kept source file lineage in the `source_file` column for auditability.

## Analyst Notes

- Google is the only platform with `conversion_value`, so ROAS is available for Google but not Facebook or TikTok.
- TikTok has the most complete video funnel data, so video completion analysis is focused on TikTok.
- Facebook includes reach and frequency, making it useful for audience delivery analysis.
- The dashboard recommendations are based on standardized cross-channel KPIs rather than raw platform exports alone.
