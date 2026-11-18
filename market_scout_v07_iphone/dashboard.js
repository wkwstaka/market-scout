"use strict";

function element(tag, value, parent) {
  const node = document.createElement(tag);
  if (value !== null) node.textContent = value;
  parent.append(node);
  return node;
}

function disclosure(label, parent) {
  const details = element("details", null, parent);
  element("summary", label, details);
  return details;
}

async function loadOpportunities() {
  const status = document.getElementById("opportunityStatus");
  const container = document.getElementById("opportunities");
  try {
    const response = await fetch("./data/opportunities.json", {cache: "no-cache"});
    if (!response.ok) throw new Error("Report unavailable");
    const report = await response.json();
    const counts = report.counts;
    const date = report.collected_at
      ? new Date(report.collected_at).toLocaleString("ja-JP", {timeZone: "Asia/Tokyo"})
      : "未収集";
    const errors = report.feed_status.filter(feed => feed.status !== "ok").length;
    status.textContent = `最終収集 ${date}（日本時間）｜${counts.total}件中${counts.matched}件採用、${counts.excluded}件除外、${counts.duplicates}件重複`
      + (errors ? `｜取得エラー ${errors}件。過去の収集分を含みます。` : "");
    if (!report.top_five.length) {
      element("p", "条件を満たす調査候補はありません。", container);
    }
    report.top_five.forEach((candidate, index) => {
      const card = element("article", null, container);
      card.className = "item lead";
      element("h3", `${index + 1}. ${candidate.name}`, card);
      element("p", `調査優先度 ${candidate.research_priority}/3 · 事業評価 要調査`, card);

      const sources = element("ul", null, disclosure("根拠の見出しと選別理由", card));
      candidate.evidence.forEach(evidence => {
        const item = element("li", null, sources);
        const url = new URL(evidence.url);
        if (url.protocol === "https:") {
          const link = element("a", evidence.title, item);
          link.href = url.href;
          link.target = "_blank";
          link.rel = "noopener noreferrer";
        }
        const published = evidence.published ? evidence.published.slice(0, 10) : "日付不明";
        element("small", ` ${published}｜${evidence.relevance.join("・")}｜${evidence.reason}`, item);
      });

      const scoring = element("ul", null, disclosure("評価項目と必要なデータ", card));
      candidate.dimensions.forEach(dimension => {
        const value = dimension.points ?? "要調査";
        element("li", `${dimension.name}（配点${dimension.max_points}）${value} · ${dimension.needed}`, scoring);
      });

      const experiment = element("ul", null, disclosure("7日間の検証案", card));
      candidate.experiment.forEach(step => element("li", step, experiment));
    });
  } catch {
    container.replaceChildren();
    status.textContent = "レポートを読み込めませんでした。時間をおいて再読み込みしてください。";
  }
}

loadOpportunities();
