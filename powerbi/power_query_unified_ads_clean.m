let
    CsvPath = "C:\Users\hieum\Desktop\Repo\Senior_Marketing_Analyst\Senior Marketing Analyst\data\unified_ads_clean.csv",
    Source = Csv.Document(
        File.Contents(CsvPath),
        [
            Delimiter = ",",
            Columns = 35,
            Encoding = 65001,
            QuoteStyle = QuoteStyle.Csv
        ]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    ChangedTypes = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"date", type date},
            {"platform", type text},
            {"campaign_id", type text},
            {"campaign_name", type text},
            {"objective", type text},
            {"ad_group_id", type text},
            {"ad_group_name", type text},
            {"impressions", Int64.Type},
            {"clicks", Int64.Type},
            {"spend", Currency.Type},
            {"conversions", Int64.Type},
            {"conversion_value", Currency.Type},
            {"video_views", Int64.Type},
            {"video_watch_25", Int64.Type},
            {"video_watch_50", Int64.Type},
            {"video_watch_75", Int64.Type},
            {"video_watch_100", Int64.Type},
            {"likes", Int64.Type},
            {"shares", Int64.Type},
            {"comments", Int64.Type},
            {"reach", Int64.Type},
            {"frequency", type number},
            {"quality_score", type number},
            {"search_impression_share", Percentage.Type},
            {"engagements", Int64.Type},
            {"engagement_rate", Percentage.Type},
            {"ctr", Percentage.Type},
            {"cpc", Currency.Type},
            {"cpm", Currency.Type},
            {"cvr", Percentage.Type},
            {"cpa", Currency.Type},
            {"roas", type number},
            {"video_view_rate", Percentage.Type},
            {"video_completion_rate", Percentage.Type},
            {"source_file", type text}
        }
    ),
    AddedCampaignDisplayName = Table.AddColumn(
        ChangedTypes,
        "campaign_display_name",
        each Text.Replace([campaign_name], "_", " "),
        type text
    ),
    AddedAdGroupDisplayName = Table.AddColumn(
        AddedCampaignDisplayName,
        "ad_group_display_name",
        each Text.Replace([ad_group_name], "_", " "),
        type text
    )
in
    AddedAdGroupDisplayName
