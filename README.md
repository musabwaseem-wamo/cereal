# CerealBox AI Studio

This project is a local prototype for the CerealBox Agency AI automation challenge. Its custom Flask, HTML, CSS and JavaScript interface runs on your computer; nothing is deployed.

## What this project does

Each of the nine challenge workflows has its own section, arranged in a guided sequence:

1. **AI Idea Generator:** generate five distinct concepts with an audience insight, strategic rationale, core message, execution, test hypothesis, goal-aligned KPI and evidence to verify. One is labeled as an objective-based recommended starting point, not a performance prediction.
2. **AI Copywriting:** select an idea and generate hooks, headlines and primary text. Choose a primary-text variant to carry into the landing-page preview and download.
3. **AI Landing Pages:** preview and download a responsive, standalone HTML page with the offer details and selected ad-copy variant carried through. The product-style artwork is illustrative, not a generated product image.
4. **AI Static Creative:** build an editable image prompt from the brief, selected idea, visual direction and aspect ratio. Copy it to an external image model; this app does not render images.
5. **AI Script Writing:** generate a continuous 15-, 30-, 45- or 60-second script, then regenerate with a runtime improvement request. OpenAI mode applies the request; local-template mode attaches it as a clearly labeled production note.
6. **AI UGC Video:** build a copyable creator-style video prompt and shot outline with claim-safety guidance. It does not generate video.
7. **AI Video Editing:** split timed script scenes into an edit-ready clip timeline and split individual clips at their midpoint. This is text-only; it does not edit footage or render a video.
8. **AI Media Buyer / Ads Agent:** get a rule-based launch plan, daily budget allocation, success metrics and guardrails from the campaign brief. This planning section is separate from results reporting and cannot control ad accounts.
9. **Toast / Meta Ads Analysis:** view sample CSV metrics, recommendations, a ROAS bar chart and a conversion-share chart.

No live advertising accounts are connected. The Meta demo reveals the bundled CSV; it does not authenticate or retrieve live data. The landing-page export is a single HTML file with embedded CSS; review its placeholder button links, product details and claims before publishing. Approved campaign snapshots are saved in this browser's local storage and can be reopened from **Approved drafts** in the sidebar or top bar. Choose **Edit draft** to reopen one in the studio; regenerate the campaign after changing its brief, then **Save changes & approve** to replace the archived version. After approval, choose **Start new campaign** to return to the brief form; the approved snapshot stays archived. Drafts are not uploaded or published. OpenAI use requires an API key and internet access, and may incur charges.

## Project structure

```text
cerealbox-ai-studio/
├── README.md
├── pyproject.toml
├── uv.lock
├── .env.example
├── .gitignore
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── data/
│   │   ├── mock_ads.csv
│   │   └── sample_campaigns.json
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── analytics.py
│   │   ├── editing.py
│   │   ├── generators.py
│   │   ├── landing_export.py
│   │   ├── llm_service.py
│   │   ├── media_buyer.py
│   │   └── ugc_prompt.py
│   ├── static/
│   │   ├── app.js
│   │   └── styles.css
│   ├── templates/
│   │   └── index.html
│   └── utils/
│       ├── __init__.py
│       └── prompts.py
├── docs/
│   ├── PROJECT_EXPLANATION.md
│   ├── WORKFLOW_MAP.md
│   └── ROADMAP.md
└── tests/
│   ├── test_generators.py
│   └── test_web_app.py
```

## Quick start with uv

This project uses `uv` for dependency management.

1. Install uv if needed:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Create and sync the local environment:

```bash
cd cerealbox-ai-studio
uv venv
uv sync
```

3. Configure the OpenAI API key locally if you do not already have `.env`:

```bash
test -f .env || cp .env.example .env
```

If you created `.env` already, keep it; do not overwrite it. Otherwise, edit `.env` and replace the example value with your key. `.env` is ignored by git and must not be shared or committed. The app can run without a key using local demo templates. If an OpenAI request fails (for example, because a key is invalid or unavailable), the campaign ideas, selected-idea ad copy, video script or edit timeline falls back to local demo output rather than interrupting the demo; the source label identifies the fallback. Successful OpenAI requests may incur API charges.

4. Start the app locally:

```bash
uv run python -m app.main
```

5. Open `http://127.0.0.1:5000` in your browser. The server binds to your computer only. Keep the terminal open while using the app and press Ctrl+C to stop it.

## Demo flow

The app is a local, end-to-end workflow prototype:

1. Enter a campaign brief and generate campaign concepts.
2. Select an idea and use the workflow navigation to continue to ad copy. Review the hooks, headlines and body-copy variants; the selected primary text carries into the next page.
3. Review the landing-page preview and download its standalone HTML draft.
4. Continue in order through **AI Static Creative**, **AI Script Writing**, **AI UGC Video**, **AI Video Editing**, and **AI Media Buyer**. Each page has previous/next controls; direct tabs remain available too.
5. In **Toast / Meta Analysis**, click **Connect to Meta (demo)** to reveal the sample report and charts; all displayed data comes from the included CSV.
6. Use **Approve draft** to open the completion review for the eight required campaign-building steps. Each step is listed as complete or incomplete, with a shortcut to unfinished work; confirm approval once all required steps are complete. Human review and Toast / Meta Ads Analysis are optional. Find approved snapshots from **Approved drafts** in the sidebar or top bar; use **Edit draft** to reopen a snapshot and **Save changes & approve** to replace its archived version. After approval, **Start new campaign** returns to the brief form while keeping the snapshot in the archive. They remain in this browser only and are not published.

The left navigation sidebar can be expanded on desktop and tablet with its chevron control. The workspace shifts over to preserve the layout rather than being covered; on narrow phones it stays compact to keep room for the page.

## Challenge coverage

This app covers the required CerealBox challenge areas in a practical, mock environment:

- AI Copywriting
- AI Static Creative
- AI Script Writing
- AI UGC Video
- AI Video Editing (script-to-timeline splitting only; no footage processing)
- AI Media Buyer / Ads Agent
- AI Idea Generator
- AI Landing Pages
- Toast / Meta Ads Analysis

## Quality controls included

- brand input and constraints
- human approval checklist
- policy-safe guidance inside the brief
- mock performance dashboard to guide recommendation logic

## Notes

This is a prototype to show thinking, workflow design and practical implementation. It is not a full production-ready agency platform, but it is structured in a way that can be extended into a real AI automation system over time. Running the local app sends campaign-generation prompts to OpenAI when a valid API key is configured; do not enter confidential client information into this demo.
