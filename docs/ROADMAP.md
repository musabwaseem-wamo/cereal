# 90-Day Roadmap

## Current prototype status

Implemented:
- Separate sections for all nine workflows
- Campaign ideas, selected-idea copy and duration-specific video scripts (OpenAI when configured; labeled local templates otherwise)
- Static image and creator-video prompt builders
- Runtime script revision instructions
- Script-to-edit-timeline splitting with additional midpoint split actions
- Brief-based media plan with budget allocation and guardrails, separate from reporting
- A selected copy variant carried into the landing-page preview and standalone HTML export
- Mock-data ad metrics, recommendations, ROAS bars and conversion-share chart
- Reversible, session-only draft approval control
- Meta demo action that reveals sample CSV reporting data

Still proposed or illustrative:
- Finished image/video generation and footage editing/rendering
- Live Meta or Toast connections (the in-app Meta action only reveals demo data)
- Automated actions in ad accounts
- Published landing pages and persistent approvals (current approval status is not saved)

## Weeks 1-2: validate the proof of concept

Focus:
- define campaign brief model
- test the idea and copy generation with several sample briefs
- review the rule-based dashboard recommendations with agency stakeholders
- validate with 2-3 sample campaigns

Deliverables:
- documented examples and acceptance criteria for idea/copy quality
- confirmed KPI definitions and recommendation rules for reporting

Success measure:
- users can trace every generated recommendation back to the brief or sample data and can identify outputs requiring human review

## Days 15-30: creative and landing page expansion

Focus:
- add static creative concept generation
- add script + UGC video concepts
- generate landing page drafts from selected angle
- add human review checklist and stronger prompt constraints

Deliverables:
- completed creative pipeline
- candidate ad concepts and script variations
- landing page mockup based on selected campaign idea

Success measure:
- a campaign can move from brief to page and asset concepts without manual rework

## Days 30-60: analysis and agent workflow

Focus:
- build AI recommendations from ad data
- add alert logic and Meta/Toast style reporting
- define rules for budget reallocation and performance warnings
- connect creative reporting back to briefs

Deliverables:
- functioning ads agent workflow
- dashboard with trend detection and recommendations
- data-driven recommendations for future asset generation

Success measure:
- the system identifies obvious campaign patterns and suggests practical next steps

## Days 60-90: scale, governance and reuse

Focus:
- strengthen prompt management and templates
- build reusable workflows per client vertical
- create a small content library and asset history
- document quality controls and governance rules

Deliverables:
- modular system that can handle multiple campaigns or clients
- templates for recurring campaign types
- maintainable architecture and documentation

Success measure:
- new campaigns can be launched with less manual setup and stronger quality control

## Why the order matters

The highest-value first milestone is the idea + copy + analysis loop because it shows tangible business value quickly. Once that is working, layer in creative and page generation, then ad optimisation logic and governance.
