# Data Dictionary and Schema Mapping

This file explains how the three source ad tables are merged into one clean cross-channel reporting table.

## Source Tables

| Platform | Source file | Original spend field | Original ad group field | Notes |
|---|---|---|---|---|
| Facebook | `data/01_facebook_ads.csv` | `spend` | `ad_set_id`, `ad_set_name` | Includes reach, frequency, video views, and engagement rate |
| Google | `data/02_google_ads.csv` | `cost` | `ad_group_id`, `ad_group_name` | Includes conversion value, CTR, CPC, quality score, and search impression share |
| TikTok | `data/03_tiktok_ads.csv` | `cost` | `adgroup_id`, `adgroup_name` | Includes video watch milestones, likes, shares, and comments |

## Unified Field Mapping

| Unified field | Facebook source | Google source | TikTok source | Cleaning logic |
|---|---|---|---|---|
| `date` | `date` | `date` | `date` | Kept as ISO date text |
| `platform` | Added as `Facebook` | Added as `Google` | Added as `TikTok` | Added during normalization |
| `campaign_id` | `campaign_id` | `campaign_id` | `campaign_id` | Required field |
| `campaign_name` | `campaign_name` | `campaign_name` | `campaign_name` | Required field |
| `objective` | Inferred from campaign name | Inferred from campaign name | Inferred from campaign name | Creates readable strategy categories |
| `ad_group_id` | `ad_set_id` | `ad_group_id` | `adgroup_id` | Standardized naming |
| `ad_group_name` | `ad_set_name` | `ad_group_name` | `adgroup_name` | Standardized naming |
| `impressions` | `impressions` | `impressions` | `impressions` | Converted to non-negative number |
| `clicks` | `clicks` | `clicks` | `clicks` | Converted to non-negative number |
| `spend` | `spend` | `cost` | `cost` | Standardized into one spend field |
| `conversions` | `conversions` | `conversions` | `conversions` | Converted to non-negative number |
| `conversion_value` | blank | `conversion_value` | blank | Only Google has tracked revenue in this dataset |
| `video_views` | `video_views` | blank | `video_views` | Used for video view rate |
| `video_watch_25` | blank | blank | `video_watch_25` | TikTok-specific video funnel |
| `video_watch_50` | blank | blank | `video_watch_50` | TikTok-specific video funnel |
| `video_watch_75` | blank | blank | `video_watch_75` | TikTok-specific video funnel |
| `video_watch_100` | blank | blank | `video_watch_100` | Used for completion rate |
| `likes`, `shares`, `comments` | blank | blank | TikTok fields | Used to calculate TikTok engagements |
| `reach` | `reach` | blank | blank | Facebook-specific reach |
| `frequency` | `frequency` | blank | blank | Facebook-specific frequency |
| `quality_score` | blank | `quality_score` | blank | Google-specific diagnostic metric |
| `search_impression_share` | blank | `search_impression_share` | blank | Google-specific competitive metric |
| `source_file` | file name | file name | file name | Preserves data lineage |

## Calculated KPI Formulas

| KPI | Formula | Business use |
|---|---|---|
| `ctr` | `clicks / impressions` | Measures click engagement |
| `cpc` | `spend / clicks` | Measures traffic efficiency |
| `cpm` | `spend * 1000 / impressions` | Measures media cost efficiency |
| `cvr` | `conversions / clicks` | Measures conversion quality after click |
| `cpa` | `spend / conversions` | Main efficiency metric for conversion campaigns |
| `roas` | `conversion_value / spend` | Revenue return, available where conversion value exists |
| `video_view_rate` | `video_views / impressions` | Measures video reach quality |
| `video_completion_rate` | `video_watch_100 / video_views` | Measures video creative retention |
| `engagement_rate` | `engagements / impressions` when source rate is unavailable | Measures social engagement quality |

## Cleaning Rules

- Blank numeric values are preserved as blanks when a platform does not track that field.
- Numeric source values are converted to non-negative numbers.
- KPI rates are recalculated from raw counts for consistency.
- Required fields are `date`, `campaign_id`, `campaign_name`, and ad group ID.
- Duplicate rows are merged at the `date + platform + campaign_id + ad_group_id` grain.
- Additive metrics are summed during duplicate merging.
- Diagnostic averages such as `frequency`, `quality_score`, and `search_impression_share` are averaged if duplicates exist.
