const data = window.DASHBOARD_DATA;

const colors = {
  Facebook: "#3167b1",
  Google: "#008b84",
  TikTok: "#d95d4f",
  Awareness: "#3167b1",
  Conversion: "#008b84",
  Retargeting: "#2f7d4f",
  Traffic: "#c98b17",
  Search: "#7258b5",
  Shopping: "#d95d4f",
  Influencer: "#20242a",
};

const fmtCurrency = (value, compactOrOptions = false) => {
  const options =
    typeof compactOrOptions === "object"
      ? compactOrOptions
      : { compact: compactOrOptions };
  const compact = options.compact || false;
  const digits = options.digits ?? (compact ? 1 : 0);
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: compact ? 0 : digits,
    maximumFractionDigits: digits,
    notation: compact ? "compact" : "standard",
  }).format(value || 0);
};

const fmtNumber = (value, compact = false) =>
  new Intl.NumberFormat("en-US", {
    maximumFractionDigits: compact ? 1 : 0,
    notation: compact ? "compact" : "standard",
  }).format(value || 0);

const fmtPct = (value, digits = 1) =>
  value == null ? "n/a" : `${(value * 100).toFixed(digits)}%`;

const fmtRate = (value, digits = 2) => (value == null ? "n/a" : value.toFixed(digits));

const escapeHtml = (value) =>
  String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");

const byPlatform = (platform) => data.platforms.find((item) => item.platform === platform);
const maxOf = (items, key) => Math.max(...items.map((item) => item[key] || 0), 1);
const platformColor = (platform) => colors[platform] || "#607080";

function renderHeader() {
  const range = data.source.date_range;
  document.getElementById("periodLabel").textContent =
    `${range.start} to ${range.end} | ${range.days} reporting days | Facebook, Google, and TikTok`;
  document.getElementById("generatedDate").textContent =
    `Clean build: ${data.generated_at}`;
}

function renderKpis() {
  const google = byPlatform("Google");
  const tiktok = byPlatform("TikTok");
  const kpis = [
    {
      label: "Total spend",
      value: fmtCurrency(data.totals.spend, true),
      detail: `${fmtCurrency(data.totals.cpa, { digits: 2 })} blended CPA`,
    },
    {
      label: "Impressions",
      value: fmtNumber(data.totals.impressions, true),
      detail: `${fmtPct(data.totals.ctr)} blended CTR`,
    },
    {
      label: "Clicks",
      value: fmtNumber(data.totals.clicks, true),
      detail: `${fmtCurrency(data.totals.cpc, { digits: 2 })} blended CPC`,
    },
    {
      label: "Conversions",
      value: fmtNumber(data.totals.conversions, true),
      detail: `${fmtPct(data.totals.cvr)} click-to-conversion rate`,
    },
    {
      label: "Tracked revenue",
      value: fmtCurrency(data.totals.conversion_value, true),
      detail: `Google ROAS ${fmtRate(google?.roas)}x`,
    },
    {
      label: "Video completion",
      value: fmtPct(tiktok?.video_completion_rate),
      detail: "TikTok completed-view rate",
    },
  ];

  const grid = document.getElementById("kpiGrid");
  grid.innerHTML = kpis
    .map(
      (kpi) => `
      <article class="kpi-card">
        <p class="kpi-label">${escapeHtml(kpi.label)}</p>
        <p class="kpi-value">${escapeHtml(kpi.value)}</p>
        <p class="kpi-detail">${escapeHtml(kpi.detail)}</p>
      </article>
    `,
    )
    .join("");
}

function renderChannelScorecard() {
  const maxSpend = maxOf(data.platforms, "spend");
  const target = document.getElementById("channelScorecard");
  target.innerHTML = data.platforms
    .map((platform) => {
      const width = Math.max(8, (platform.spend / maxSpend) * 100);
      return `
        <div class="score-row">
          <div class="platform-name">
            <span class="dot" style="background:${platformColor(platform.platform)}"></span>
            ${escapeHtml(platform.platform)}
          </div>
          <div class="meter" aria-hidden="true">
            <span style="width:${width}%;background:${platformColor(platform.platform)}"></span>
          </div>
          <div class="metric-stack">
            <strong>${fmtCurrency(platform.spend, true)}</strong>
            <div class="row-meta">Spend</div>
          </div>
          <div class="metric-stack">
            <strong>${fmtNumber(platform.conversions, true)}</strong>
            <div class="row-meta">Conversions</div>
          </div>
          <div class="metric-stack">
            <strong>${fmtCurrency(platform.cpa, { digits: 2 })}</strong>
            <div class="row-meta">CPA</div>
          </div>
        </div>
      `;
    })
    .join("");
}

function renderInsights() {
  const list = document.getElementById("insightList");
  list.innerHTML = data.insights
    .map(
      (insight) => `
      <li>
        <strong>${escapeHtml(insight.label)}</strong>
        <span>${escapeHtml(insight.text)}</span>
      </li>
    `,
    )
    .join("");
}

function drawDailyTrend() {
  const rows = data.daily;
  const width = 980;
  const height = 320;
  const pad = { top: 24, right: 42, bottom: 44, left: 64 };
  const plotW = width - pad.left - pad.right;
  const plotH = height - pad.top - pad.bottom;
  const maxSpend = maxOf(rows, "spend");
  const maxConversions = maxOf(rows, "conversions");
  const barW = plotW / rows.length - 4;

  const xFor = (index) => pad.left + index * (plotW / (rows.length - 1));
  const ySpend = (value) => pad.top + plotH - (value / maxSpend) * plotH;
  const yConv = (value) => pad.top + plotH - (value / maxConversions) * plotH;

  const grid = [0, 0.25, 0.5, 0.75, 1]
    .map((tick) => {
      const y = pad.top + plotH - plotH * tick;
      return `<line class="grid-line" x1="${pad.left}" x2="${width - pad.right}" y1="${y}" y2="${y}"></line>`;
    })
    .join("");

  const bars = rows
    .map((row, index) => {
      const x = pad.left + index * (plotW / rows.length) + 2;
      const y = ySpend(row.spend);
      const h = pad.top + plotH - y;
      return `<rect x="${x.toFixed(2)}" y="${y.toFixed(2)}" width="${barW.toFixed(2)}" height="${h.toFixed(2)}" rx="3" fill="#c98b17" opacity="0.74"></rect>`;
    })
    .join("");

  const linePoints = rows
    .map((row, index) => `${xFor(index).toFixed(2)},${yConv(row.conversions).toFixed(2)}`)
    .join(" ");

  const circles = rows
    .filter((_, index) => index % 5 === 0 || index === rows.length - 1)
    .map((row) => {
      const index = rows.indexOf(row);
      return `<circle cx="${xFor(index).toFixed(2)}" cy="${yConv(row.conversions).toFixed(2)}" r="4" fill="#008b84"></circle>`;
    })
    .join("");

  const xLabels = [0, Math.floor(rows.length / 2), rows.length - 1]
    .map((index) => {
      const label = rows[index].date.slice(5);
      return `<text class="axis-label" x="${xFor(index)}" y="${height - 12}" text-anchor="middle">${label}</text>`;
    })
    .join("");

  document.getElementById("dailyTrend").innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" aria-hidden="true">
      ${grid}
      ${bars}
      <polyline points="${linePoints}" fill="none" stroke="#008b84" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"></polyline>
      ${circles}
      <text class="axis-label" x="${pad.left}" y="18" text-anchor="start">Spend max ${fmtCurrency(maxSpend)}</text>
      <text class="axis-label" x="${width - pad.right}" y="18" text-anchor="end">Conversions max ${fmtNumber(maxConversions)}</text>
      ${xLabels}
    </svg>
  `;
}

function drawCampaignMatrix() {
  const rows = data.campaigns;
  const width = 760;
  const height = 400;
  const pad = { top: 24, right: 24, bottom: 56, left: 62 };
  const plotW = width - pad.left - pad.right;
  const plotH = height - pad.top - pad.bottom;
  const maxCpa = maxOf(rows, "cpa") * 1.08;
  const maxConversions = maxOf(rows, "conversions") * 1.08;
  const maxSpend = maxOf(rows, "spend");
  const xFor = (value) => pad.left + (value / maxCpa) * plotW;
  const yFor = (value) => pad.top + plotH - (value / maxConversions) * plotH;

  const points = rows
    .map((row) => {
      const radius = 7 + Math.sqrt((row.spend || 0) / maxSpend) * 15;
      const name = row.campaign_name.replaceAll("_", " ");
      return `
        <g>
          <circle
            cx="${xFor(row.cpa).toFixed(2)}"
            cy="${yFor(row.conversions).toFixed(2)}"
            r="${radius.toFixed(2)}"
            fill="${platformColor(row.platform)}"
            opacity="0.78"
          ></circle>
          <title>${escapeHtml(`${row.platform}: ${name} | CPA ${fmtCurrency(row.cpa, { digits: 2 })} | ${fmtNumber(row.conversions)} conversions`)}</title>
        </g>
      `;
    })
    .join("");

  const labels = rows
    .slice(0, 5)
    .map((row) => {
      const name = row.campaign_name.replaceAll("_", " ");
      return `<text class="chart-label" x="${xFor(row.cpa) + 12}" y="${yFor(row.conversions) - 9}">${escapeHtml(name)}</text>`;
    })
    .join("");

  document.getElementById("campaignMatrix").innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" aria-hidden="true">
      <line class="grid-line" x1="${pad.left}" x2="${pad.left}" y1="${pad.top}" y2="${pad.top + plotH}"></line>
      <line class="grid-line" x1="${pad.left}" x2="${pad.left + plotW}" y1="${pad.top + plotH}" y2="${pad.top + plotH}"></line>
      <line class="grid-line" x1="${xFor(maxCpa / 2)}" x2="${xFor(maxCpa / 2)}" y1="${pad.top}" y2="${pad.top + plotH}"></line>
      <line class="grid-line" x1="${pad.left}" x2="${pad.left + plotW}" y1="${yFor(maxConversions / 2)}" y2="${yFor(maxConversions / 2)}"></line>
      ${points}
      ${labels}
      <text class="axis-label" x="${pad.left + plotW / 2}" y="${height - 14}" text-anchor="middle">Higher CPA</text>
      <text class="axis-label" x="18" y="${pad.top + plotH / 2}" text-anchor="middle" transform="rotate(-90 18 ${pad.top + plotH / 2})">More conversions</text>
      <text class="axis-label" x="${pad.left}" y="${height - 36}" text-anchor="start">$0</text>
      <text class="axis-label" x="${pad.left + plotW}" y="${height - 36}" text-anchor="end">${fmtCurrency(maxCpa)}</text>
      <text class="axis-label" x="${pad.left + 4}" y="${pad.top + 12}" text-anchor="start">${fmtNumber(maxConversions)} conv.</text>
    </svg>
  `;
}

function renderVideoFunnel() {
  const tiktok = byPlatform("TikTok");
  const items = [
    ["25% watched", tiktok.video_watch_25 / tiktok.video_views],
    ["50% watched", tiktok.video_watch_50 / tiktok.video_views],
    ["75% watched", tiktok.video_watch_75 / tiktok.video_views],
    ["100% watched", tiktok.video_watch_100 / tiktok.video_views],
  ];

  document.getElementById("videoFunnel").innerHTML = items
    .map(([label, value], index) => {
      const color = ["#3167b1", "#008b84", "#c98b17", "#d95d4f"][index];
      return `
        <div class="progress-row">
          <div class="progress-label">${escapeHtml(label)}</div>
          <div class="progress-bar"><span style="width:${Math.max(value * 100, 4)}%;background:${color}"></span></div>
          <div class="row-meta">${fmtPct(value)}</div>
        </div>
      `;
    })
    .join("");
}

function renderObjectiveMix() {
  const maxSpend = maxOf(data.objectives, "spend");
  document.getElementById("objectiveMix").innerHTML = data.objectives
    .map((objective) => {
      const width = Math.max(6, (objective.spend / maxSpend) * 100);
      const color = colors[objective.objective] || "#607080";
      return `
        <div class="progress-row">
          <div>
            <div class="progress-label">${escapeHtml(objective.objective)}</div>
            <div class="row-meta">${fmtNumber(objective.conversions, true)} conversions</div>
          </div>
          <div class="progress-bar"><span style="width:${width}%;background:${color}"></span></div>
          <div class="row-meta">${fmtCurrency(objective.spend, true)}</div>
        </div>
      `;
    })
    .join("");
}

function renderCampaignTable() {
  const body = document.getElementById("campaignTable");
  body.innerHTML = data.campaigns
    .map(
      (campaign) => `
      <tr>
        <td><span class="platform-pill" style="color:${platformColor(campaign.platform)}">${escapeHtml(campaign.platform)}</span></td>
        <td>${escapeHtml(campaign.campaign_name.replaceAll("_", " "))}</td>
        <td>${escapeHtml(campaign.objective)}</td>
        <td class="num">${fmtCurrency(campaign.spend)}</td>
        <td class="num">${fmtNumber(campaign.conversions)}</td>
        <td class="num">${fmtCurrency(campaign.cpa, { digits: 2 })}</td>
        <td class="num">${fmtPct(campaign.ctr)}</td>
        <td class="num">${fmtPct(campaign.cvr)}</td>
        <td class="num">${campaign.roas == null ? "n/a" : `${fmtRate(campaign.roas)}x`}</td>
      </tr>
    `,
    )
    .join("");
}

function renderQuality() {
  const source = data.source;
  document.getElementById("dataQuality").innerHTML = `
    <span><strong>${source.raw_rows}</strong> source rows</span>
    <span><strong>${source.clean_rows}</strong> cleaned unified rows</span>
    <span><strong>${source.duplicates_merged}</strong> duplicates merged</span>
    <span><strong>${source.missing_required_rows_dropped}</strong> rows dropped for missing required fields</span>
    <span><strong>${source.source_files.join(", ")}</strong></span>
  `;
}

function renderDashboard() {
  renderHeader();
  renderKpis();
  renderChannelScorecard();
  renderInsights();
  drawDailyTrend();
  drawCampaignMatrix();
  renderVideoFunnel();
  renderObjectiveMix();
  renderCampaignTable();
  renderQuality();
}

renderDashboard();
