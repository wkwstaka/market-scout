import json
import unittest

from analyze import ROOT, analyze


def article(title, suffix):
    return {"title": title, "url": f"https://news.google.com/rss/articles/{suffix}"}


class AnalyzeTest(unittest.TestCase):
    def test_empty_and_irrelevant(self):
        report = analyze({"items": [article("デジタル商品券の販売開始", "coupon"),
                                    article("映画公開のお知らせ", "film")]})
        self.assertEqual(report["top_five"], [])
        self.assertEqual(report["counts"]["excluded"], 2)

    def test_deduplication_across_publishers_and_rss_queries(self):
        report = analyze({"items": [
            article("ＲＰＡ導入事例 - A", "story?oc=1"),
            article("RPA導入事例 - B", "syndicated"),
            article("RPA活用事例 - C", "story?oc=5"),
        ]})
        self.assertEqual(report["counts"]["duplicates"], 2)
        self.assertEqual(len(report["top_five"][0]["evidence"]), 1)

    def test_stronger_headline_prioritized_commercial_unknowns_stay_null(self):
        report = analyze({"items": [article("RPA導入事例", "automation"),
                                    article("中小企業白書：DX", "survey")]})
        self.assertEqual([row["id"] for row in report["top_five"]], ["adoption", "automation"])
        for candidate in report["top_five"]:
            self.assertIsNone(candidate["opportunity_score"])
            self.assertTrue(all(d["points"] is None for d in candidate["dimensions"]))
            self.assertEqual(sum(d["max_points"] for d in candidate["dimensions"]), 100)

    def test_six_qualifying_themes_are_capped_at_five(self):
        titles = ["RPA導入事例", "DX人材研修", "中小企業白書：DX", "デジタル商品の移行",
                  "YouTube収益化", "レガシーシステムのDX対策"]
        items = [article(title, index) for index, title in enumerate(titles)]
        report = analyze({"items": items})
        self.assertEqual(report["counts"]["matched"], 6)
        self.assertEqual(len(report["top_five"]), 5)

    def test_repository_snapshot_is_accounted_for(self):
        research = json.loads((ROOT / "data/research.json").read_text(encoding="utf-8"))
        report = analyze(research)
        counts = report["counts"]
        self.assertEqual(counts["total"], counts["matched"] + counts["excluded"] + counts["duplicates"])
        for candidate in report["top_five"]:
            self.assertTrue(candidate["evidence"])
            self.assertTrue(all(source["relevance"] for source in candidate["evidence"]))


if __name__ == "__main__":
    unittest.main()
