# Market Scout v0.7 — GitHub Pages + scheduled RSS discovery

## What works
- v0.6 candidate scoring, experiment logging, research queue and JSON backups, all browser-local.
- `scout.py`: fetches four Japanese Google News RSS searches; stores deduplicated, explicitly unverified news leads in `data/research.json`.
- GitHub Actions: manual trigger or daily scheduled execution around 07:15 JST (GitHub may delay/skip schedules). Commits refreshed JSON to the repository.
- iPhone dashboard loads the JSON from the same Pages origin. No API key needed.

## Publish from iPhone (public repository)
1. Create a **public** GitHub repository named `market-scout` (or use your existing one).
2. Upload **all contents** of this ZIP to the repository root, preserving `.github/workflows/research.yml`, `data/research.json`, `scout.py`, `index.html`. GitHub's mobile web uploader may not handle folder trees well; desktop upload or a GitHub-compatible Git client may be easier.
3. In Settings > Pages choose **Deploy from a branch**, branch `main`, folder `/(root)`, Save.
4. In Actions > Daily market evidence collection > Run workflow > Run workflow. Check the run log. It should update `data/research.json` and commit it; then wait for Pages to redeploy.
5. Visit `https://YOUR-USERNAME.github.io/market-scout/` in iPhone Safari. Replace YOUR-USERNAME with your own GitHub username. The URL is an example until published.
6. If commit fails due to permissions, in Settings > Actions > General > Workflow permissions allow **Read and write permissions**, then retry. Some organizations restrict this.

## Limits and safeguards
- Public repository means research JSON and all committed files are public. **Never upload credentials, private sales records, customer data, or API keys**.
- GitHub Pages is static; browser-local experiments do not sync between devices. Back up with JSON export.
- News RSS is a discovery input only; does not validate demand, customer willingness to pay, profitability, or sources. Google News article links may redirect.
- No LLM analysis, autonomous business decisions, outreach, purchase, account creation, or sales tracking is implemented. No claims of actual revenue.
- GitHub scheduled workflows may be disabled after inactivity and are not guaranteed to execute on time.

## Next stage v0.8
Server-side LLM research synthesis with cited evidence, human approval gates, strict spend caps, and private data store. Never put LLM secrets into browser JS or public JSON.
