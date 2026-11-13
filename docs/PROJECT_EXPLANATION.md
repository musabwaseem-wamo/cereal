# Project Explanation

This project is built for the CerealBox Agency candidate challenge. The purpose is to show how we would design an AI-powered agency workflow that supports creative production, campaign execution, reporting and iteration.

## Goal of the project

We are not trying to make a perfect production system in a few hours. Instead, we are building a clear demo that proves the following:

- we can turn a business brief into campaign strategy
- we can generate advertising assets with AI
- we can connect outputs into one coherent pipeline
- we can design human review checkpoints
- we can show how performance data feeds back into the next creative cycle

## What the app demonstrates

The studio has a separate section for each of the nine challenge workflows:

1. **AI Idea Generator:** five strategically differentiated concepts with audience insight, rationale, core message, execution, test hypothesis, goal-aligned KPI and evidence check. A transparent, rule-based objective match marks one as the recommended starting point; it is guidance to compare, not a prediction of results.
2. **AI Copywriting:** the selected idea and brief are sent in a separate request to generate hooks, headlines and primary text. The user can choose a body-copy variant for the landing page.
3. **AI Landing Pages:** previews and downloads a responsive standalone HTML landing page carrying the offer and chosen ad-copy variant. Decorative product-style artwork is illustrative rather than a rendered product image.
4. **AI Static Creative:** creates an editable image-model prompt from the brief, selected idea, visual direction and aspect ratio. It does not render images.
5. **AI Script Writing:** generates continuous timed scenes for a selected 15-, 30-, 45- or 60-second length. A runtime improvement request guides OpenAI regeneration; in local-template mode it is attached as a production note rather than misrepresented as AI revision.
6. **AI UGC Video:** builds a copyable external video prompt with a creator format, shot outline, claims safeguards and disclosure reminder. It does not generate video.
7. **AI Video Editing:** requires a source video, reads its duration and samples three frames in the browser. When OpenAI is configured, only the three still frames, their timestamps, duration, optional timed-script context and edit notes are sent for a visual summary, three targeted edit recommendations and a continuous edit plan. The original video stays local; users can preview the cuts and split clips locally, but the prototype does not render or export a modified video. Without AI access, it labels the generic demo timeline and does not claim to analyze the frames.
8. **AI Media Buyer / Ads Agent:** generates a rule-based campaign launch plan and daily budget split from the brief and planned budget. It is separate from results reporting and cannot control ad accounts.
9. **Toast / Meta Ads Analysis:** calculates performance metrics and recommendations from the included CSV and visualizes campaign ROAS and conversion share. It does not connect to Meta or Toast.

After generating a campaign, the nine workflow steps are ideas, copywriting, landing pages, static creative, script writing, UGC video, video editing, media buyer and ads analysis. Overview remains a separate starting tab, and Human review remains available as a separate optional tab; neither is counted as a workflow step. The idea and copywriting continue actions preserve their required generation and copy-selection steps.

The draft header includes an **Approve draft** control. Selecting it opens a completion review that lists the required steps as complete or incomplete, with shortcuts to unfinished steps. Approval can be confirmed only after a campaign idea is selected, ad copy is generated and selected, a landing page is prepared, and the static creative prompt, video script, UGC prompt, edit timeline and media plan are built. Changing the campaign brief or a step's inputs requires regenerating that output. Human review and Toast / Meta Ads Analysis remain optional. Approval saves a snapshot, including completion state, in browser local storage. After approval, **Start new campaign** returns to the editable brief form while preserving the approved archive entry. The **Approved drafts** archive is available from the sidebar and top bar, and lists snapshots even after another campaign is generated or the page is refreshed. Choose **Edit draft** to reopen a snapshot in the studio; regenerate the campaign after changing its brief, then use **Save changes & approve** to replace the archived copy. The archive remains unchanged until that save. Revoking the current approval removes the campaign from the archive. This is local to the browser and does not publish or launch the work. In reporting, **Connect to Meta (demo)** reveals the bundled sample report. It is not Meta OAuth and does not access a live account.

The landing-page export is a single `.html` file with embedded CSS. The prototype uses a same-page placeholder for its buttons; replace those destinations in the downloaded file before launch. The page uses neutral, brief-based copy rather than promising outcomes; review offer terms, product facts and all claims before publishing.

OpenAI-backed requests require a configured API key and internet access, and successful requests may incur charges. Without a key, labeled local templates are used; if an OpenAI request or response fails, campaign ideas, copy, scripts and edit plans fall back to local demo output with a source label instead of interrupting the workflow. Prompt builders are local. Nothing is published or changed automatically.

In **Toast / Meta Ads Analysis**, **Connect to Meta (demo)** reveals the bundled sample report in a clearly labeled demo state. It is not Meta OAuth and does not access a live account.

The landing-page preview can be downloaded as a single `.html` file. Its CSS is embedded, so it does not depend on Flask, Jinja templates, external stylesheets, or JavaScript to display. Buttons use a same-page placeholder destination that should be replaced in the downloaded file before launch.

For static creative, the user can choose one of the proposed image directions and an aspect ratio, then build and copy a detailed image-model prompt. It includes the campaign brief and selected campaign concept where available, with explicit instructions to avoid invented product details, unsupported claims, and generated text/logos. Any image model can be used; the prototype itself does not generate image files.

This prototype demonstrates a possible agency workflow: brief first, creative drafts next, sample performance review after that. It does not automate or publish a real campaign.

## Why this approach is strong

This project makes the interview story easier to explain because it follows the same flow a real agency team would follow:

1. Define the brief
2. Generate ideas
3. Create creative options
4. Shortlist the best direction
5. Build a landing page or direct response flow
6. Review performance data
7. Improve the next campaign cycle

## Project design

The app is purposely lightweight and usable without API keys or paid subscriptions. The focus is on clarity and extensibility instead of dependency-heavy tooling.

### Core logic

- `app/main.py` serves the local Flask app and JSON endpoints
- `app/templates/index.html` defines the campaign studio interface
- `app/static/` contains the local CSS and browser-side JavaScript
- `app/modules/llm_service.py` makes separate structured OpenAI requests for campaign ideas, selected-idea copy, duration-specific video scripts and three-frame video edit plans; validates responses; and labels local fallbacks if no key exists
- `app/modules/generators.py` creates local text examples for the proposed creative and page workflows
- `app/modules/landing_export.py` creates an escaped, standalone HTML export with embedded CSS
- `app/modules/image_prompt.py` builds reusable, aspect-ratio-aware prompts for external image models
- `app/modules/ugc_prompt.py` builds creator-style prompts for external video tools
- `app/modules/editing.py` supports deterministic script-to-clip timeline splitting
- `app/modules/media_buyer.py` creates brief-based planning recommendations, separate from reporting
- `app/modules/analytics.py` calculates mock KPI summaries and recommendations
- `app/data/mock_ads.csv` provides sample ad performance data

## Interview-ready story

If you present this to the founder, the message should be:

'We are not building isolated AI experiments. We are designing a campaign operating system for an agency, where an AI model helps with ideation, creative generation and reporting, while humans retain strategic and approval responsibility at the right checkpoints.'

That is exactly the kind of practical thinking the challenge is looking for.
