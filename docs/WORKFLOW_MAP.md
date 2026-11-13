# Workflow Map

This document explains the end-to-end agency workflow behind the project.

## 1. AI Copywriting

Input: campaign intent, target audience, offer and brand tone

Workflow:
- capture the brief
- generate hooks, angles and headline variations
- rank the strongest options by clarity, fit and conversion focus
- send the chosen set to human review

Human review:
- brand alignment
- legal or ethical safety
- CTA clarity

Current prototype: selecting a concept generates hooks, headlines and primary text. Choose a primary-text variant to carry into the landing-page draft.

## 2. AI Static Creative

Input: ad copy + product visuals + brand tone

Workflow:
- generate multiple static ad concepts
- choose a proposed visual direction and aspect ratio
- build a detailed prompt containing the campaign brief and selected idea, ready to paste into any external image model
- generate the actual image in the user's chosen image tool; the prototype does not render image files
- test across selected channels
- shortlist the best option with a designer review

Human review:
- brand consistency
- product accuracy
- design quality and campaign fit

Current prototype: a detailed prompt builder uses the brief, selected idea, direction and aspect ratio. Paste the result into an external image model; no image is rendered in this app.

## 3. AI Script Writing

Input: campaign goal, audience and product benefits

Workflow:
- produce short-form video scripts
- tailor for hooks, product action, proof and CTA
- regenerate with a runtime improvement request

Human review:
- pacing and realism
- brand voice
- claims and compliance

Current prototype: exact 15-, 30-, 45- or 60-second timed text. OpenAI mode applies the improvement request; local-template mode adds it as a clearly labeled production note.

## 4. AI UGC Video

Input: script + creator persona + style constraints

Workflow:
- create creator-style concept directions
- suggest scenes, framing and on-screen text
- propose B-roll or shot list variations
- build a model-agnostic prompt for an external video model or creator brief

Human review:
- authenticity
- comfort and fit for creator personas
- performance style requirements

Current prototype: choose a creator format and aspect ratio to produce a prompt and shot outline. It explicitly avoids invented personal testimonials, claims and results; it does not generate video.

## 5. AI Video Editing

Input: required local source video, its runtime, three sampled still frames, optional timed script, and editing notes

Workflow:
- sample frames near the beginning, middle, and end of the source
- return a visual summary and three focused edit suggestions grounded in those samples
- suggest a continuous clip plan grounded in those visual samples and the source runtime
- split an individual clip again at its midpoint
- optionally use a timed script for voiceover and on-screen text
- attach editing notes to the resulting timeline
- preview the proposed cut sequence against the local source video with captions and a campaign brand mark

Human review:
- verify AI observations and choose final cut points against the full footage
- check pacing and continuity
- apply captions, transitions, branding and final export in a media editor

Current prototype: the browser extracts the video duration and three still frames. When configured, OpenAI analyzes those frames—not the full video or its audio—and returns a visual summary, three focused edit suggestions, and a duration-matched continuous edit plan. Only the sampled stills, timestamps, duration, optional script and edit notes are sent to the AI; the original video remains local. The timeline can be previewed and split in the browser but is not rendered or exported.

## 6. AI Media Buyer / Ads Agent

Input: campaign brief, objective and planned daily budget

Workflow:
- suggest a goal-aligned budget split across prospecting, retargeting or test reserves
- define a primary success metric
- propose a controlled creative test and review actions
- state operational and measurement guardrails

Human review:
- budget risk
- strategic direction
- final execution decisions

Current prototype: a rule-based planning assistant only. It is intentionally separate from Toast / Meta reporting and cannot create, pause or edit campaigns.

## 7. AI Idea Generator

Input: market context, offer and audience pain points

Workflow:
- generate campaign hooks, product claims and angle concepts
- produce reasoned alternatives based on audience behaviour
- feed winners into copy and creative workflows

Human review:
- originality and brand fit
- creative quality and differentiation

Current prototype: five distinct testable concepts are generated from the campaign brief; selecting one feeds copy and creative workflows.

## 8. AI Landing Pages

Input: selected winning idea + offer + CTA

Workflow:
- create hero section, value proposition and body copy
- produce layout idea and CTA structure
- include the selected ad-copy headline and body text
- download a standalone HTML draft

Human review:
- offer accuracy
- conversion quality
- design polish

Current prototype: preview and single-file HTML download. Publishing and analytics integration are not included.

## 9. Toast / Meta Ads Analysis

Input: campaign metrics and creative performance data

Workflow:
- track recurring patterns across ad sets or campaigns
- identify issues such as rising CPC, weak CTR or creative fatigue
- recommend next moves and report findings in a dashboard
- visualize sample ROAS and conversion share by campaign

Human review:
- strategic interpretation
- commercial decision making
- validation with broader business context

Current prototype: metrics, recommendations and charts use the included CSV only. The demo Meta action does not connect to a live account.

## Full system view

The real agency system is not one giant model doing everything. It is a connected workflow where each step has a clear owner and a human review checkpoint.

That architecture is what makes the system practical, maintainable and scalable.
