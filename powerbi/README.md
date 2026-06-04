# Power BI Build Package

This folder turns the cleaned cross-channel ads CSV into a Power BI-ready dashboard build.

## Source Data

Use this file as the Power BI source:

`../data/unified_ads_clean.csv`

The cleaned table has 330 rows at the daily platform + campaign + ad group grain.

## PBIX File

Open the finished Power BI dashboard here:

`dashboard.pbix`

## Recommended Setup

1. Open Power BI Desktop.
2. Select **Get data > Text/CSV**.
3. Import `data/unified_ads_clean.csv`.
4. Rename the imported table to `Ads`.
5. In Power Query, confirm the data types listed in `power_query_unified_ads_clean.m`.
6. Load the table.
7. Add measures from `measures.dax`, or run `tabular_editor_create_measures.csx` in Tabular Editor to create them in one pass.
8. Import `senior_marketing_analyst_theme.json` from **View > Themes > Browse for themes**.

## Fast Measure Import

Power BI Desktop does not have a classic "import all measures from a DAX file" button, but newer builds can add multiple measures through **DAX Query View**:

1. Open the **DAX Query View** icon on the left rail.
2. Paste the contents of `dax_query_view_create_measures.dax`.
3. Click **Run**.
4. Click **Update model with changes**.
5. Return to Report/Table view and confirm the measures appear under `Ads`.

This native route creates the main measures in one pass. It does not create the optional `Video Funnel Stage` table or measure formatting.

For the fuller automated setup, use Tabular Editor:

1. Install Tabular Editor.
2. Keep the PBIX open in Power BI Desktop.
3. Go to **External Tools > Tabular Editor**.
4. In Tabular Editor, open **Advanced Scripting**. Do not paste the `.csx` file into DAX Query View or the DAX editor.
5. Paste the contents of `tabular_editor_create_measures.csx`.
6. Click **Run**.
7. Click **Save** in Tabular Editor.
8. Return to Power BI Desktop and refresh the Fields/Data pane if needed.

The Tabular Editor script creates or updates all measures, creates the optional video funnel table, applies formats, and keeps measures in display folders.

## Dashboard Pages

### Page 1: Executive Dashboard

Use the same business flow as the static dashboard:

| Area | Power BI visual | Fields |
|---|---|---|
| KPI cards | Card visuals | Total Spend, Total Impressions, Total Clicks, Total Conversions, Tracked Revenue, Video Completion Rate |
| Channel scorecard | Matrix or clustered bar | Platform, Total Spend, Total Conversions, Blended CPA |
| Daily trend | Line and clustered column chart | Axis: date; Column: Total Spend; Line: Total Conversions |
| Campaign efficiency | Scatter chart | X: Blended CPA; Y: Total Conversions; Size: Total Spend; Legend: platform; Details: campaign_display_name |
| Video funnel | Bar chart | Axis: Video Funnel Stage[Stage]; Value: Video Funnel Rate |
| Objective mix | Donut or treemap | Legend: objective; Value: Total Spend |
| Campaign table | Table visual | platform, campaign_display_name, objective, Total Spend, Total Conversions, Blended CPA, Blended CTR, Blended CVR, Blended ROAS |

### Page 2: Campaign Detail

Add slicers for `date`, `platform`, `objective`, and `campaign_display_name`. Use a campaign table plus KPI cards so recruiters can audit the numbers behind the executive recommendations.

## Formatting

- Total Spend, Blended CPA, Blended CPC, Blended CPM, and Tracked Revenue: Currency.
- Blended CTR, Blended CVR, Engagement Rate, Video View Rate, Video Completion Rate, Spend Share: Percent.
- Blended ROAS: Decimal number.
- Total Impressions, Total Clicks, Total Conversions, Total Video Views, Total Engagements: Whole number.
- Sort the campaign table by CPA ascending or Conversions descending depending on the story.

## Notes

- Google is the only platform with tracked conversion value in this dataset, so ROAS is most meaningful when filtered to Google.
- Blank platform-specific fields should stay blank/null rather than converted to zero unless they are additive metrics.
- The Power BI site is currently separate from the GitHub Pages static dashboard. This package is for creating a `.pbix` in Power BI Desktop.
