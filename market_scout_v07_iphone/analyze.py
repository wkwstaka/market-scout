"""Rank public RSS leads for follow-up without inferring commercial results."""
import html
import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent

# Each hypothesis requires both a subject and a concrete signal in the headline.
THEMES = (
    ("automation", "バックオフィスの業務自動化",
     r"業務自動化|バックオフィス|rpa|ワークフロー",
     r"事例|ツール|販売|導入|ocr|チャットボット",
     "バックオフィス担当者", "手作業1件を自動化する試作"),
    ("skills", "中小企業のDX人材育成",
     r"dx|デジタル化", r"人材|研修|採用難|育成",
     "中小企業のDX担当者", "実務課題を使った短時間の研修"),
    ("adoption", "中小企業のDX導入支援",
     r"中小企業|企業のdx", r"白書|動向調査|導入|コンサル|デジタル化",
     "中小企業の経営者", "既存業務と導入候補を整理する診断"),
    ("migration", "デジタル商品の販路移行",
     r"デジタル商品|artstation|gumroad", r"移行|販売|終了",
     "デジタル素材の出品者", "商品情報と販売リンクの移行チェックリスト"),
    ("creators", "クリエイターの収益導線の見直し",
     r"クリエイター|youtube|tiktok", r"収益化|収益分配|報酬|収益機会",
     "動画やSNSの制作者", "既存の収益導線を見直す診断シート"),
    ("legacy", "レガシー業務システムの棚卸し",
     r"レガシーシステム|モダン化", r"dx|対策|導入|移行",
     "既存システムの運用担当者", "移行対象と手作業の棚卸しシート"),
)

EXCLUDE = re.compile(r"商品券|応援券|プレミアム付|銘柄|資格\d*選|上場会見|オンライン】|開催.*入門")
SIGNALS = (
    (3, r"白書|動向調査|最新調査|業務委託|企画提案", "調査・公募への言及"),
    (2, r"活用事例|導入事例|販売開始|移行|終了|募集|事例", "導入事例・提供・制度変更への言及"),
    (1, r".", "関連する見出し"),
)
DIMENSIONS = (
    ("需要", 30, "対象顧客への聞き取りと有償申込"),
    ("収益性", 25, "提示価格と提供にかかる原価・工数"),
    ("自動化適性", 20, "対象作業の再現性・例外・手動確認の工数"),
    ("初期費用", 15, "試作と導入に必要な費用・時間"),
    ("継続性", 10, "利用頻度と再購入・継続利用の記録"),
)


def analyze(research):
    grouped = {theme[0]: [] for theme in THEMES}
    counts = dict(total=len(research["items"]), matched=0, excluded=0, duplicates=0)
    seen_titles, seen_urls = set(), set()
    for item in research["items"]:
        title = item.get("title") or ""
        url = item.get("url") or ""
        headline = unicodedata.normalize("NFKC", html.unescape(title.rsplit(" - ", 1)[0])).casefold()
        link = urlsplit(url)
        if link.scheme != "https" or not link.hostname or EXCLUDE.search(headline):
            counts["excluded"] += 1
            continue
        theme = next((rule for rule in THEMES
                      if re.search(rule[2], headline) and re.search(rule[3], headline)), None)
        if theme is None:
            counts["excluded"] += 1
            continue
        normalized_title = re.sub(r"[\W_]+", "", headline)
        url_key = (link.netloc, link.path, "" if link.hostname == "news.google.com" else link.query)
        if normalized_title in seen_titles or url_key in seen_urls:
            counts["duplicates"] += 1
            continue
        seen_titles.add(normalized_title)
        seen_urls.add(url_key)
        score, _, reason = next(rule for rule in SIGNALS if re.search(rule[1], headline))
        grouped[theme[0]].append(dict(title=title, url=url, published=item.get("published"),
                                     relevance=[re.search(theme[2], headline)[0],
                                                re.search(theme[3], headline)[0]],
                                     score=score, reason=reason))
        counts["matched"] += 1

    candidates = []
    for key, name, _, _, audience, offer in THEMES:
        evidence = sorted(grouped[key], key=lambda row: (-row["score"], row["title"], row["url"]))
        if not evidence:
            continue
        candidates.append(dict(
            id=key, name=name, research_priority=evidence[0]["score"], evidence=evidence[:3],
            opportunity_score=None,
            dimensions=[dict(name=label, max_points=weight, points=None, needed=needed)
                        for label, weight, needed in DIMENSIONS],
            experiment=[
                f"1–2日目：{audience}に現状の作業、頻度、代替手段を聞く。",
                f"3–4日目：{offer}を下書きし、試作時間と提供原価を見積もる。",
                "5–6日目：承認後、聞き取り協力者に試案と仮価格を提示し、回答と有償申込数を記録する。",
                "7日目：提示人数、回答、申込、実費、作業時間を集計し、継続判断を記録する。",
            ],
        ))
    candidates.sort(key=lambda row: (-row["research_priority"], row["id"]))
    return dict(schema_version="0.8", collected_at=research.get("generated_at"),
                feed_status=research.get("feed_status", []), counts=counts, top_five=candidates[:5])


if __name__ == "__main__":
    research = json.loads((ROOT / "data/research.json").read_text(encoding="utf-8"))
    report = analyze(research)
    (ROOT / "data/opportunities.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(report["counts"])
