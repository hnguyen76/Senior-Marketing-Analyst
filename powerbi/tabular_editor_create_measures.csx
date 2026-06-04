// IMPORTANT: This is a C# Advanced Scripting script for Tabular Editor.
// Do not paste this file into Power BI DAX Query View, DAX Studio, or a New measure formula bar.
// If you are in Power BI DAX Query View, use dax_query_view_create_measures.dax instead.
//
// Tabular Editor script for the Senior Marketing Analyst Power BI model.
// Open the PBIX in Power BI Desktop, then External Tools > Tabular Editor.
// In Tabular Editor: Advanced Scripting > paste/run this script > Save.

var ads = Model.Tables["Ads"];

void UpsertMeasure(string name, string expression, string formatString, string folder)
{
    var measure = ads.Measures.Contains(name)
        ? ads.Measures[name]
        : ads.AddMeasure(name, expression, folder);

    measure.Expression = expression;
    measure.FormatString = formatString;
    measure.DisplayFolder = folder;
}

if (!ads.Columns.Contains("campaign_display_name"))
{
    ads.AddCalculatedColumn(
        "campaign_display_name",
        @"SUBSTITUTE ( Ads[campaign_name], ""_"", "" "" )"
    );
}

if (!ads.Columns.Contains("ad_group_display_name"))
{
    ads.AddCalculatedColumn(
        "ad_group_display_name",
        @"SUBSTITUTE ( Ads[ad_group_name], ""_"", "" "" )"
    );
}

UpsertMeasure(
    "Total Spend",
    @"SUM ( Ads[spend] )",
    @"$#,0;($#,0);-",
    "Executive KPIs"
);

UpsertMeasure(
    "Total Impressions",
    @"SUM ( Ads[impressions] )",
    @"#,0",
    "Executive KPIs"
);

UpsertMeasure(
    "Total Clicks",
    @"SUM ( Ads[clicks] )",
    @"#,0",
    "Executive KPIs"
);

UpsertMeasure(
    "Total Conversions",
    @"SUM ( Ads[conversions] )",
    @"#,0",
    "Executive KPIs"
);

UpsertMeasure(
    "Tracked Revenue",
    @"SUM ( Ads[conversion_value] )",
    @"$#,0;($#,0);-",
    "Executive KPIs"
);

UpsertMeasure(
    "Blended CTR",
    @"DIVIDE ( [Total Clicks], [Total Impressions] )",
    @"0.0%",
    "Efficiency Rates"
);

UpsertMeasure(
    "Blended CPC",
    @"DIVIDE ( [Total Spend], [Total Clicks] )",
    @"$#,0.00;($#,0.00);-",
    "Efficiency Rates"
);

UpsertMeasure(
    "Blended CPM",
    @"DIVIDE ( [Total Spend] * 1000, [Total Impressions] )",
    @"$#,0.00;($#,0.00);-",
    "Efficiency Rates"
);

UpsertMeasure(
    "Blended CVR",
    @"DIVIDE ( [Total Conversions], [Total Clicks] )",
    @"0.0%",
    "Efficiency Rates"
);

UpsertMeasure(
    "Blended CPA",
    @"DIVIDE ( [Total Spend], [Total Conversions] )",
    @"$#,0.00;($#,0.00);-",
    "Efficiency Rates"
);

UpsertMeasure(
    "Blended ROAS",
    @"DIVIDE ( [Tracked Revenue], [Total Spend] )",
    @"0.00x",
    "Efficiency Rates"
);

UpsertMeasure(
    "Total Video Views",
    @"SUM ( Ads[video_views] )",
    @"#,0",
    "Video and Engagement"
);

UpsertMeasure(
    "Video View Rate",
    @"DIVIDE ( [Total Video Views], [Total Impressions] )",
    @"0.0%",
    "Video and Engagement"
);

UpsertMeasure(
    "Video Completion Rate",
    @"DIVIDE ( SUM ( Ads[video_watch_100] ), [Total Video Views] )",
    @"0.0%",
    "Video and Engagement"
);

UpsertMeasure(
    "Total Engagements",
    @"SUM ( Ads[engagements] )",
    @"#,0",
    "Video and Engagement"
);

UpsertMeasure(
    "Engagement Rate",
    @"DIVIDE ( [Total Engagements], [Total Impressions] )",
    @"0.0%",
    "Video and Engagement"
);

UpsertMeasure(
    "Spend Share",
    @"DIVIDE (
    [Total Spend],
    CALCULATE ( [Total Spend], ALL ( Ads[platform] ) )
)",
    @"0.0%",
    "Efficiency Rates"
);

UpsertMeasure(
    "Average Frequency",
    @"AVERAGE ( Ads[frequency] )",
    @"0.00",
    "Diagnostics"
);

UpsertMeasure(
    "Average Quality Score",
    @"AVERAGE ( Ads[quality_score] )",
    @"0.0",
    "Diagnostics"
);

UpsertMeasure(
    "Average Search Impression Share",
    @"AVERAGE ( Ads[search_impression_share] )",
    @"0.0%",
    "Diagnostics"
);

UpsertMeasure(
    "Campaign Rank by CPA",
    @"RANKX (
    ALLSELECTED ( Ads[campaign_display_name] ),
    [Blended CPA],
    ,
    ASC,
    DENSE
)",
    @"0",
    "Campaign Prioritization"
);

UpsertMeasure(
    "Campaign Rank by Conversions",
    @"RANKX (
    ALLSELECTED ( Ads[campaign_display_name] ),
    [Total Conversions],
    ,
    DESC,
    DENSE
)",
    @"0",
    "Campaign Prioritization"
);

UpsertMeasure(
    "CPA Efficiency Band",
    @"SWITCH (
    TRUE (),
    ISBLANK ( [Blended CPA] ), ""No conversions"",
    [Blended CPA] <= 8, ""Scale / protect"",
    [Blended CPA] <= 15, ""Monitor"",
    ""Optimize / reduce""
)",
    @"",
    "Campaign Prioritization"
);

if (!Model.Tables.Contains("Video Funnel Stage"))
{
    Model.AddCalculatedTable(
        "Video Funnel Stage",
        @"DATATABLE (
    ""Stage"", STRING,
    ""Sort"", INTEGER,
    {
        { ""25% watched"", 1 },
        { ""50% watched"", 2 },
        { ""75% watched"", 3 },
        { ""100% watched"", 4 }
    }
)"
    );
}

UpsertMeasure(
    "Video Funnel Rate",
    @"SWITCH (
    SELECTEDVALUE ( 'Video Funnel Stage'[Stage] ),
    ""25% watched"", DIVIDE ( SUM ( Ads[video_watch_25] ), [Total Video Views] ),
    ""50% watched"", DIVIDE ( SUM ( Ads[video_watch_50] ), [Total Video Views] ),
    ""75% watched"", DIVIDE ( SUM ( Ads[video_watch_75] ), [Total Video Views] ),
    ""100% watched"", DIVIDE ( SUM ( Ads[video_watch_100] ), [Total Video Views] )
)",
    @"0.0%",
    "Video and Engagement"
);

if (Model.Tables.Contains("Video Funnel Stage"))
{
    var funnel = Model.Tables["Video Funnel Stage"];
    if (funnel.Columns.Contains("Stage") && funnel.Columns.Contains("Sort"))
    {
        funnel.Columns["Stage"].SortByColumn = funnel.Columns["Sort"];
    }
}
