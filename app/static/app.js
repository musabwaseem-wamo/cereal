const form = document.querySelector("#brief-form");
const toast = document.querySelector("#toast");
const editVideoUpload = document.querySelector("#edit-video-upload");
const editVideoPreview = document.querySelector("#edit-video-preview");
const editVideoStage = document.querySelector("#edit-video-stage");
const editVideoSourceStatus = document.querySelector("#edit-video-source-status");
const previewEditButton = document.querySelector("#preview-edit-timeline");
const buildEditButton = document.querySelector("#build-edit-timeline");
const editAnalysisSummary = document.querySelector("#edit-visual-analysis-summary");
const editSuggestionsPanel = document.querySelector("#edit-suggestions-panel");
const editSuggestionsList = document.querySelector("#edit-suggestions-list");
const MAX_EDIT_VIDEO_BYTES = 100 * 1024 * 1024;
const MAX_EDIT_VIDEO_DURATION_SECONDS = 180;
let toastTimer;
let currentBrief = null;
let selectedIdea = null;
let selectedLandingCopy = null;
let currentVideoScript = null;
let editingClips = [];
let editVideoObjectUrl = null;
let editVideoDuration = null;
let editVideoLoadError = false;
let editVideoErrorMessage = "";
let activePreviewClipIndex = -1;
let previewEditSequence = false;
let staticCreativeDirections = [];
let draftApproved = false;
let currentDraftId = null;
let editingApprovedDraftId = null;
let currentCampaignData = null;
let approvedDrafts = [];
let completedCampaignSteps = new Set();
const APPROVED_DRAFTS_STORAGE_KEY = "cerealbox-approved-drafts-v1";
const requiredCampaignSteps = [
  ["ideas", "Choose a campaign idea"],
  ["copy", "Generate and select ad copy"],
  ["landing", "Prepare the landing page"],
  ["creative", "Build the static creative prompt"],
  ["script", "Generate the video script"],
  ["ugc", "Build the UGC video prompt"],
  ["editing", "Build the video edit timeline"],
  ["media", "Create the media plan"],
];
const workflowOrder = [
  ["ideas", "Campaign ideas"],
  ["copy", "AI Copywriting"],
  ["landing", "AI Landing Pages"],
  ["creative", "AI Static Creative"],
  ["script", "AI Script Writing"],
  ["ugc", "AI UGC Video"],
  ["editing", "AI Video Editing"],
  ["media", "AI Media Buyer"],
  ["ads", "Toast / Meta Ads Analysis"],
];

function showToast(message, isError = false) {
  toast.textContent = message;
  toast.classList.toggle("error", isError);
  toast.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("show"), 3600);
}

function loadApprovedDrafts() {
  try {
    const stored = localStorage.getItem(APPROVED_DRAFTS_STORAGE_KEY);
    if (stored === null) return [];
    const parsed = JSON.parse(stored);
    if (!Array.isArray(parsed)) throw new TypeError("Approved drafts storage must be a list.");
    return parsed.filter((draft) =>
      draft &&
      typeof draft.id === "string" &&
      typeof draft.approvedAt === "string" &&
      typeof draft.title === "string" &&
      typeof draft.brand === "string" &&
      typeof draft.summary === "string"
    );
  } catch (error) {
    console.error("Could not load approved drafts from this browser.", error);
    showToast("Could not load approved drafts saved in this browser.", true);
    return [];
  }
}

function saveApprovedDrafts(drafts) {
  try {
    localStorage.setItem(APPROVED_DRAFTS_STORAGE_KEY, JSON.stringify(drafts));
    approvedDrafts = drafts;
    renderApprovedDrafts();
    return true;
  } catch (error) {
    console.error("Could not save approved drafts in this browser.", error);
    showToast("Could not save this approval in browser storage. Check available storage and try again.", true);
    return false;
  }
}

function appendDetail(parent, label, value) {
  if (!value) return;
  const row = document.createElement("div");
  row.className = "approved-draft-detail";
  const term = document.createElement("strong");
  term.textContent = label;
  const description = document.createElement("p");
  description.textContent = value;
  row.append(term, description);
  parent.append(row);
}

function renderApprovedDrafts() {
  const container = document.querySelector("#approved-drafts-list");
  const count = document.querySelector("#approved-drafts-count");
  const navCount = document.querySelector("#approved-drafts-nav-count");
  if (!container || !count) return;
  count.textContent = String(approvedDrafts.length);
  navCount.textContent = String(approvedDrafts.length);
  container.replaceChildren();
  if (approvedDrafts.length === 0) {
    const empty = document.createElement("p");
    empty.className = "approved-drafts-empty";
    empty.textContent = "No approved drafts yet. Approve a campaign draft to save it here.";
    container.append(empty);
    return;
  }

  [...approvedDrafts].reverse().forEach((draft) => {
    const card = document.createElement("article");
    card.className = "approved-draft-card";
    const heading = document.createElement("div");
    heading.className = "approved-draft-card-heading";
    const title = document.createElement("h3");
    title.textContent = draft.title;
    const badge = document.createElement("span");
    badge.className = "approved-draft-badge";
    badge.textContent = "Approved";
    heading.append(title, badge);
    const meta = document.createElement("p");
    meta.className = "approved-draft-meta";
    const approvedDate = new Date(draft.approvedAt);
    meta.textContent = `${draft.brand} · Approved ${Number.isNaN(approvedDate.getTime()) ? "date unavailable" : approvedDate.toLocaleString()}`;
    const summary = document.createElement("p");
    summary.className = "approved-draft-summary";
    summary.textContent = draft.summary;
    card.append(heading, meta, summary);

    const details = document.createElement("details");
    details.className = "approved-draft-more";
    const summaryLabel = document.createElement("summary");
    summaryLabel.textContent = "View approved campaign details";
    const detailContent = document.createElement("div");
    detailContent.className = "approved-draft-details";
    appendDetail(detailContent, "Product or service", draft.brief?.product);
    appendDetail(detailContent, "Audience", draft.brief?.audience);
    appendDetail(detailContent, "Offer", draft.brief?.offer);
    appendDetail(detailContent, "Campaign goal", draft.brief?.goal);
    appendDetail(detailContent, "Channel", draft.brief?.channel);
    appendDetail(detailContent, "Primary CTA", draft.brief?.cta);
    appendDetail(detailContent, "Brand voice", draft.brief?.tone);
    appendDetail(detailContent, "Requirements", draft.brief?.constraints);
    appendDetail(detailContent, "Landing page headline", draft.campaign?.landing_page?.hero);
    appendDetail(detailContent, "Landing page subhead", draft.campaign?.landing_page?.subhead);
    appendDetail(detailContent, "Landing page benefits", draft.campaign?.landing_page?.bullets?.join("\n"));
    appendDetail(detailContent, "Static creative directions", draft.campaign?.static_creatives?.join("\n\n"));
    appendDetail(detailContent, "UGC concepts", draft.campaign?.video?.ugc_ideas?.join("\n\n"));
    if (draft.idea) {
      appendDetail(detailContent, "Selected idea", draft.idea.title);
      appendDetail(detailContent, "Strategic angle", draft.idea.strategic_angle);
    }
    if (draft.campaign?.ideas?.length) {
      const ideas = document.createElement("details");
      const ideasSummary = document.createElement("summary");
      ideasSummary.textContent = `All ${draft.campaign.ideas.length} campaign ideas`;
      ideas.append(ideasSummary);
      draft.campaign.ideas.forEach((idea) => {
        const ideaCard = document.createElement("div");
        ideaCard.className = "approved-draft-idea";
        appendDetail(ideaCard, "Idea", idea.title);
        appendDetail(ideaCard, "Audience insight", idea.audience_insight);
        appendDetail(ideaCard, "Strategic angle", idea.strategic_angle);
        appendDetail(ideaCard, "Why test this", idea.strategic_rationale);
        appendDetail(ideaCard, "Core message", idea.core_message);
        appendDetail(ideaCard, "Creative execution", idea.creative_execution);
        appendDetail(ideaCard, "Test hypothesis", idea.test_hypothesis);
        appendDetail(ideaCard, "Primary KPI", idea.primary_kpi);
        appendDetail(ideaCard, "Verify before launch", idea.evidence_to_confirm);
        ideas.append(ideaCard);
      });
      detailContent.append(ideas);
    }
    if (draft.adCopy) {
      appendDetail(detailContent, "Selected ad headline", draft.adCopy.headline);
      appendDetail(detailContent, "Selected ad copy", draft.adCopy.body);
    }
    if (draft.script?.length) {
      appendDetail(detailContent, "Video script", draft.script.map((scene) =>
        `${scene.start_seconds}–${scene.end_seconds}s: ${scene.beat} — ${scene.voiceover}`
      ).join("\n"));
    }
    details.append(summaryLabel, detailContent);
    card.append(details);
    const actions = document.createElement("div");
    actions.className = "approved-draft-actions";
    const edit = document.createElement("button");
    edit.type = "button";
    edit.className = "button button-outline";
    edit.textContent = "Edit draft";
    edit.addEventListener("click", () => loadApprovedDraftForEditing(draft));
    actions.append(edit);
    card.append(actions);
    container.append(card);
  });
}

function updateApprovalAvailability() {
  const button = document.querySelector("#approval-button");
  const summary = document.querySelector("#approval-review-summary");
  const list = document.querySelector("#approval-review-list");
  const confirmButton = document.querySelector("#confirm-approval-button");
  if (!button || !summary || !list || !confirmButton) return;
  const missingSteps = requiredCampaignSteps.filter(([step]) => !completedCampaignSteps.has(step));
  const briefChanged = Boolean(currentBrief && Object.entries(currentBrief).some(([name, value]) => {
    const field = form.elements.namedItem(name);
    return field && field.value !== value;
  }));
  const completeCount = requiredCampaignSteps.length - missingSteps.length;
  summary.textContent = briefChanged
    ? "The campaign brief has changed. Regenerate the campaign before approving."
    : `${completeCount} of ${requiredCampaignSteps.length} required campaign steps are complete.`;
  confirmButton.disabled = missingSteps.length > 0 || briefChanged;
  confirmButton.textContent = editingApprovedDraftId ? "Save changes & approve" : "Approve draft";
  list.replaceChildren();
  if (briefChanged) {
    const item = document.createElement("li");
    item.className = "approval-review-item incomplete";
    item.textContent = "Campaign brief — changed; regenerate campaign outputs";
    list.append(item);
  }
  requiredCampaignSteps.forEach(([step, label]) => {
    const item = document.createElement("li");
    const complete = completedCampaignSteps.has(step);
    item.className = `approval-review-item ${complete ? "complete" : "incomplete"}`;
    const status = document.createElement("span");
    status.className = "approval-review-status";
    status.textContent = complete ? "Complete" : "Incomplete";
    const name = document.createElement("span");
    name.className = "approval-review-name";
    name.textContent = label;
    item.append(status, name);
    if (!complete) {
      const goToStep = document.createElement("button");
      goToStep.type = "button";
      goToStep.className = "approval-step-link";
      goToStep.textContent = "Go to step";
      goToStep.addEventListener("click", () => {
        document.querySelector("#approval-review-dialog").close();
        showView(step);
        document.querySelector("#generated-content").scrollIntoView({ behavior: "smooth", block: "start" });
      });
      item.append(goToStep);
    }
    list.append(item);
  });
}

function setCampaignStepComplete(step, complete = true) {
  if (!complete) markCurrentDraftModified();
  if (complete) completedCampaignSteps.add(step);
  else completedCampaignSteps.delete(step);
  updateApprovalAvailability();
}

function clearCampaignStepsAfter(step) {
  const stepIndex = requiredCampaignSteps.findIndex(([key]) => key === step);
  requiredCampaignSteps.slice(stepIndex + 1).forEach(([key]) => completedCampaignSteps.delete(key));
  updateApprovalAvailability();
}

function addOutputCards(containerId, items, actionLabel = "", onAction = null) {
  const container = document.getElementById(containerId);
  container.replaceChildren();
  items.forEach((text, index) => {
    const card = document.createElement("article");
    card.className = "output-card";
    const number = document.createElement("span");
    number.className = "output-index";
    number.textContent = String(index + 1).padStart(2, "0");
    const content = document.createElement("p");
    content.className = "output-text";
    content.textContent = text;
    card.append(number, content);
    if (actionLabel && onAction) {
      const action = document.createElement("button");
      action.type = "button";
      action.className = "button button-outline output-action";
      action.textContent = actionLabel;
      action.addEventListener("click", () => onAction(text, index));
      card.append(action);
    }
    container.append(card);
  });
}

function showView(view) {
  document.querySelectorAll("[data-panel]").forEach((panel) => {
    panel.classList.toggle("hidden", panel.dataset.panel !== view);
  });
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.view === view);
  });
  document.querySelectorAll(".rail-item").forEach((item) => {
    item.classList.toggle("active", item.dataset.view === view);
  });
  updateWorkflowNavigation(view);
}

function setupWorkflowNavigation() {
  workflowOrder.forEach(([view], index) => {
    const panel = document.querySelector(`[data-panel="${view}"]`);
    const navigation = document.createElement("nav");
    navigation.className = "workflow-navigation";
    navigation.setAttribute("aria-label", `${view} workflow navigation`);
    const previous = index > 0
      ? `<button class="button button-outline workflow-previous" type="button" data-workflow-index="${index - 1}"><span aria-hidden="true">←</span> ${workflowOrder[index - 1][1]}</button>`
      : '<button class="button button-outline workflow-previous" type="button" data-workflow-view="overview"><span aria-hidden="true">←</span> Campaign overview</button>';
    const next = index < workflowOrder.length - 1
      ? `<button class="button button-coral workflow-next" type="button" data-workflow-index="${index + 1}">Continue to ${workflowOrder[index + 1][1]} <span class="button-arrow">→</span></button>`
      : '<button class="button button-outline workflow-next" type="button" data-workflow-view="review">Optional: human review <span class="button-arrow">→</span></button>';
    navigation.innerHTML = `${previous}<span class="workflow-progress">STEP ${String(index + 1).padStart(2, "0")} / ${String(workflowOrder.length).padStart(2, "0")}</span>${next}`;
    navigation.addEventListener("click", (event) => {
      const button = event.target.closest("button[data-workflow-index], button[data-workflow-view]");
      if (!button || button.disabled) return;
      const targetIndex = Number(button.dataset.workflowIndex);
      const targetView = button.dataset.workflowView || workflowOrder[targetIndex][0];
      if (view === "ideas" && targetView === "copy") {
        generateSelectedIdeaCopy();
        return;
      }
      if (view === "copy" && targetView === "landing") {
        continueToLandingPage();
        return;
      }
      showView(targetView);
      document.querySelector("#generated-content").scrollIntoView({ behavior: "smooth", block: "start" });
    });
    panel.append(navigation);
  });
  updateWorkflowNavigation("ideas");
}

function updateWorkflowNavigation(view) {
  const index = workflowOrder.findIndex(([key]) => key === view);
  if (index < 0) return;
  const navigation = document.querySelector(`[data-panel="${view}"] .workflow-navigation`);
  if (!navigation) return;
  const next = navigation.querySelector(".workflow-next");
  if (view === "ideas") {
    next.disabled = !selectedIdea;
    next.innerHTML = `Continue to ${workflowOrder[index + 1][1]} <span class="button-arrow">→</span>`;
  } else if (view === "copy") {
    next.disabled = !selectedLandingCopy || document.querySelector("#copy-results").classList.contains("hidden");
  } else if (view !== "ads") {
    next.disabled = !currentBrief;
  }
}

function renderAds(ads) {
  const summary = ads.summary;
  const metrics = [
    ["TOTAL SPEND", `$${summary.total_spend.toFixed(0)}`],
    ["AVG. CTR", `${summary.avg_ctr.toFixed(2)}%`],
    ["AVG. CPC", `$${summary.avg_cpc.toFixed(2)}`],
    ["AVG. ROAS", `${summary.avg_roas.toFixed(2)}x`],
    ["CONVERSIONS", summary.total_conversions.toLocaleString()],
  ];
  const metricGrid = document.getElementById("metric-grid");
  metricGrid.replaceChildren();
  metrics.forEach(([label, value]) => {
    const card = document.createElement("article");
    card.className = "metric-card";
    const metricLabel = document.createElement("div");
    metricLabel.className = "metric-label";
    metricLabel.textContent = label;
    const metricValue = document.createElement("div");
    metricValue.className = "metric-value";
    metricValue.textContent = value;
    card.append(metricLabel, metricValue);
    metricGrid.append(card);
  });

  const rows = document.getElementById("ads-rows");
  rows.replaceChildren();
  ads.rows.forEach((ad) => {
    const row = document.createElement("tr");
    [ad.campaign, `$${Number(ad.spend).toFixed(0)}`, Number(ad.clicks).toLocaleString(),
      `${(Number(ad.ctr) * 100).toFixed(1)}%`, `${Number(ad.roas).toFixed(1)}x`, ad.hook]
      .forEach((value) => {
        const cell = document.createElement("td");
        cell.textContent = value;
        row.append(cell);
      });
    rows.append(row);
  });
  addOutputCards("recommendations", ads.recommendations);
  renderAnalyticsCharts(ads.rows);
}

function renderAnalyticsCharts(rows) {
  const colors = ["#3567c8", "#d8a340", "#2e8b69", "#8b70bc", "#db705a"];
  const maximumRoas = Math.max(...rows.map((row) => Number(row.roas)), 1);
  const barChart = document.querySelector("#roas-chart");
  barChart.replaceChildren();
  rows.forEach((row, index) => {
    const item = document.createElement("div");
    item.className = "bar-chart-row";
    const label = document.createElement("span");
    label.className = "bar-chart-label";
    label.textContent = row.campaign;
    const track = document.createElement("span");
    track.className = "bar-chart-track";
    const bar = document.createElement("span");
    bar.className = "bar-chart-fill";
    bar.style.width = `${Math.max(4, Number(row.roas) / maximumRoas * 100)}%`;
    bar.style.backgroundColor = colors[index % colors.length];
    track.append(bar);
    const value = document.createElement("strong");
    value.textContent = `${Number(row.roas).toFixed(1)}x`;
    item.append(label, track, value);
    barChart.append(item);
  });

  const total = rows.reduce((sum, row) => sum + Number(row.conversions), 0);
  let offset = 0;
  const segments = rows.map((row, index) => {
    const share = total ? Number(row.conversions) / total * 100 : 0;
    const start = offset;
    offset += share;
    return `${colors[index % colors.length]} ${start}% ${offset}%`;
  });
  const conversionChart = document.querySelector("#conversion-chart");
  conversionChart.style.background = total
    ? `conic-gradient(${segments.join(", ")})`
    : "#dce5ef";
  document.querySelector("#conversion-chart-total").textContent =
    `${total.toLocaleString()} conversions`;
  const legend = document.querySelector("#conversion-legend");
  legend.replaceChildren();
  rows.forEach((row, index) => {
    const item = document.createElement("div");
    item.className = "chart-legend-item";
    const swatch = document.createElement("span");
    swatch.className = "chart-legend-swatch";
    swatch.style.backgroundColor = colors[index % colors.length];
    const label = document.createElement("span");
    label.textContent = `${row.campaign} · ${Number(row.conversions).toLocaleString()}`;
    item.append(swatch, label);
    legend.append(item);
  });
}

function formatSelectedIdea(idea) {
  return idea ? `${idea.title} — ${idea.strategic_angle}` : "Choose an idea in Step 1, then generate ad copy.";
}

function renderVideoScript(script, durationSeconds, source) {
  currentVideoScript = script;
  setCampaignStepComplete("script", script.length > 0);
  const scriptList = document.querySelector("#script-list");
  scriptList.replaceChildren();
  script.forEach((scene) => {
    const row = document.createElement("article");
    row.className = "script-row";
    const timing = document.createElement("span");
    timing.className = "script-time";
    const formatTime = (seconds) =>
      `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`;
    timing.textContent = `${formatTime(scene.start_seconds)}–${formatTime(scene.end_seconds)}`;
    const content = document.createElement("div");
    content.className = "script-scene";
    const heading = document.createElement("strong");
    heading.textContent = scene.beat;
    content.append(heading);
    [["Visual", scene.visual], ["Voiceover", scene.voiceover], ["On-screen text", scene.on_screen_text]]
      .filter(([, value]) => value)
      .forEach(([label, value]) => {
        const detail = document.createElement("p");
        const detailLabel = document.createElement("strong");
        detailLabel.textContent = `${label}: `;
        detail.append(detailLabel, document.createTextNode(value));
        content.append(detail);
      });
    row.append(timing, content);
    scriptList.append(row);
  });
  document.querySelector("#video-script-source").textContent =
    `${durationSeconds}-second script · ${source} · text draft only`;
  document.querySelector("#edit-timeline-source").textContent =
    `Current source: ${durationSeconds}-second script · ${script.length} scenes.`;
}

function updateLandingAdCopy(copy) {
  selectedLandingCopy = copy;
  const section = document.querySelector("#landing-ad-copy");
  const status = document.querySelector("#landing-copy-status");
  document.querySelectorAll("#primary-list .output-card").forEach((card, index) => {
    const action = card.querySelector(".output-action");
    const selected = Boolean(copy) && index === copy.index;
    card.classList.toggle("selected", selected);
    if (action) action.textContent = selected ? "Selected" : "Use on landing page";
  });
  if (!copy) {
    setCampaignStepComplete("landing", false);
    section.classList.add("hidden");
    status.textContent = "Generate ad copy and choose a primary-text variant in AI Copywriting to carry your campaign message into this page.";
    updateWorkflowNavigation("copy");
    return;
  }
  document.querySelector("#landing-ad-headline").textContent = copy.headline;
  document.querySelector("#landing-ad-body").textContent = copy.body;
  section.classList.remove("hidden");
  setCampaignStepComplete("landing", Boolean(currentCampaignData?.landing_page?.hero));
  status.textContent = `Selected ad copy for this landing page: “${copy.headline}”`;
  updateWorkflowNavigation("copy");
}

function continueToLandingPage() {
  if (!selectedLandingCopy) {
    showToast("Choose a primary-text variant before continuing to the landing page.", true);
    return;
  }
  showView("landing");
  document.querySelector("#generated-content").scrollIntoView({ behavior: "smooth", block: "start" });
}

function renderCampaign(data) {
  document.querySelector("#welcome").classList.add("hidden");
  document.querySelector("#generated-content").classList.remove("hidden");
  clearEditVideo();
  currentDraftId = editingApprovedDraftId || crypto.randomUUID();
  currentCampaignData = data;
  currentBrief = data.brief;
  selectedIdea = null;
  selectedLandingCopy = null;
  currentVideoScript = null;
  editingClips = [];
  draftApproved = false;
  completedCampaignSteps = new Set();
  document.querySelector("#result-title").textContent = `${data.brief.brand} campaign draft`;
  updateApprovalStatus();
  document.querySelector("#strategy-summary").textContent = data.summary;
  document.querySelector("#summary-source").textContent = data.summary_source;
  document.querySelector("#ideas-source").textContent = data.ideas_source;
  document.querySelector("#idea-count").textContent = `${data.ideas.length} ideas returned`;
  document.querySelector(".tab-count").textContent = String(data.ideas.length).padStart(2, "0");
  const recommendedIdeaIndex = Number.isInteger(data.recommended_idea_index)
    ? data.recommended_idea_index
    : 0;
  document.querySelector("#recommendation-reason").textContent =
    `${data.recommendation_reason || "Suggested starting point based on the campaign objective."} This is not a prediction of performance; compare all ideas before choosing.`;
  const ideasList = document.querySelector("#ideas-list");
  ideasList.replaceChildren();
  data.ideas.forEach((idea, index) => {
    const label = document.createElement("label");
    label.className = "idea-option";
    const radio = document.createElement("input");
    radio.type = "radio";
    radio.name = "selected-campaign-idea";
    radio.value = String(index);
    radio.addEventListener("change", () => {
      selectedIdea = idea;
      completedCampaignSteps.clear();
      setCampaignStepComplete("ideas");
      document.querySelector("#image-prompt-result").classList.add("hidden");
      document.querySelector("#ugc-prompt-result").classList.add("hidden");
      document.querySelector("#media-plan-result").classList.add("hidden");
      document.querySelector("#script-list").replaceChildren();
      document.querySelector("#edit-timeline").replaceChildren();
      document.querySelector("#image-prompt-text").value = "";
      document.querySelector("#ugc-prompt-text").value = "";
      document.querySelector("#video-script-source").textContent = "Choose a total duration and generate a script.";
      currentVideoScript = null;
      editingClips = [];
      document.querySelector("#edit-timeline").replaceChildren();
      document.querySelector("#edit-timeline-source").textContent =
        "Your campaign idea changed. Generate a new video edit plan to refresh the campaign context.";
      editAnalysisSummary.textContent = "";
      editAnalysisSummary.classList.add("hidden");
      clearEditSuggestions();
      stopEditPreview();
      updateEditPreviewState();
      updateLandingAdCopy(null);
      document.querySelector("#copy-results").classList.add("hidden");
      document.querySelector("#idea-selection-help").textContent = `Concept ${index + 1} selected. Continue when you're ready to generate its ad copy.`;
      document.querySelector("#copy-angle").textContent = formatSelectedIdea(idea);
      document.querySelector("#copy-source").textContent = "Waiting for selection";
      updateWorkflowNavigation("ideas");
    });
    const number = document.createElement("span");
    number.className = "idea-option-number";
    number.textContent = String(index + 1).padStart(2, "0");
    const copy = document.createElement("span");
    copy.className = "idea-option-content";
    const title = document.createElement("strong");
    title.className = "idea-option-title";
    title.textContent = idea.title;
    const titleRow = document.createElement("span");
    titleRow.className = "idea-title-row";
    titleRow.append(title);
    if (index === recommendedIdeaIndex) {
      label.classList.add("recommended");
      const badge = document.createElement("span");
      badge.className = "idea-recommended-badge";
      badge.textContent = "★ Recommended";
      titleRow.append(badge);
    }
    copy.append(titleRow);
    [
      ["Audience insight", idea.audience_insight],
      ["Strategic angle", idea.strategic_angle],
      ["Why test this", idea.strategic_rationale],
      ["Core message", idea.core_message],
      ["Creative execution", idea.creative_execution],
      ["Test hypothesis", idea.test_hypothesis],
      ["Primary KPI", idea.primary_kpi],
      ["Verify before launch", idea.evidence_to_confirm],
    ].forEach(([labelText, value]) => {
      const detail = document.createElement("span");
      detail.className = "idea-option-detail";
      if (labelText === "Primary KPI") detail.classList.add("idea-kpi");
      const detailLabel = document.createElement("strong");
      detailLabel.textContent = `${labelText}: `;
      detail.append(detailLabel, document.createTextNode(value));
      copy.append(detail);
    });
    const mark = document.createElement("span");
    mark.className = "idea-option-mark";
    mark.textContent = "Select";
    label.append(radio, number, copy, mark);
    ideasList.append(label);
  });
  document.querySelector("#idea-selection-help").textContent = "Select an idea to continue.";
  document.querySelector("#copy-results").classList.add("hidden");
  document.querySelector("#copy-progress").classList.add("hidden");
  document.querySelector("#copy-angle").textContent = "Choose an idea in Step 1, then generate ad copy.";
  document.querySelector("#copy-source").textContent = "Waiting for idea";
  updateLandingAdCopy(null);
  updateWorkflowNavigation("ideas");
  showView("ideas");
  staticCreativeDirections = data.static_creatives;
  const directionSelect = document.querySelector("#image-direction-select");
  directionSelect.replaceChildren();
  staticCreativeDirections.forEach((direction, index) => {
    const option = document.createElement("option");
    option.value = String(index);
    option.textContent = `Direction ${index + 1}`;
    directionSelect.append(option);
  });
  document.querySelector("#image-prompt-result").classList.add("hidden");
  document.querySelector("#image-prompt-text").value = "";
  addOutputCards("creative-list", data.static_creatives);
  addOutputCards("ugc-list", data.video.ugc_ideas);
  document.querySelector("#ugc-prompt-result").classList.add("hidden");
  document.querySelector("#ugc-prompt-text").value = "";
  document.querySelector("#script-list").replaceChildren();
  document.querySelector("#video-script-source").textContent = "Choose a total duration and generate a script.";
  document.querySelector("#video-progress").classList.add("hidden");
  document.querySelector("#edit-timeline").replaceChildren();
  document.querySelector("#edit-timeline-source").textContent = "Choose a video to enable frame analysis and edit suggestions.";
  editAnalysisSummary.textContent = "";
  editAnalysisSummary.classList.add("hidden");
  clearEditSuggestions();
  document.querySelector("#media-plan-result").classList.add("hidden");
  document.querySelector("#meta-connect-gate").classList.remove("hidden");
  document.querySelector("#meta-report").classList.add("hidden");

  document.querySelector("#landing-brand").textContent = data.brief.brand.toUpperCase();
  document.querySelector("#landing-footer-brand").textContent = data.brief.brand.toUpperCase();
  document.querySelector("#landing-art-brand").textContent = data.brief.brand.toUpperCase();
  document.querySelector("#landing-offer").textContent = data.brief.offer;
  document.querySelector("#landing-art-offer").textContent = data.brief.offer;
  document.querySelector("#landing-product").textContent = data.brief.product;
  document.querySelector("#landing-hero").textContent = data.landing_page.hero;
  document.querySelector("#landing-subhead").textContent = data.landing_page.subhead;
  document.querySelector("#landing-cta").textContent = data.landing_page.cta;
  ["#landing-nav-cta", "#landing-bottom-cta"].forEach((selector) => {
    const button = document.querySelector(selector);
    button.replaceChildren(document.createTextNode(data.landing_page.cta));
    const arrow = document.createElement("b");
    arrow.setAttribute("aria-hidden", "true");
    arrow.textContent = "↗";
    button.append(" ", arrow);
  });
  const benefits = document.querySelector("#landing-bullets");
  benefits.replaceChildren();
  data.landing_page.bullets.forEach((bullet) => {
    const item = document.createElement("div");
    item.className = "benefit";
    const check = document.createElement("span");
    check.textContent = "✓";
    const text = document.createElement("span");
    text.textContent = bullet;
    item.append(check, text);
    benefits.append(item);
  });
  const checklist = document.querySelector("#review-checklist");
  checklist.replaceChildren();
  data.review_checklist.forEach((item, index) => {
    const label = document.createElement("label");
    label.className = "review-item";
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.setAttribute("aria-label", `Review item ${index + 1}`);
    const text = document.createElement("span");
    text.textContent = item;
    label.append(checkbox, text);
    checklist.append(label);
  });
  renderAds(data.ads);
  updateApprovalAvailability();
  document.querySelector("#meta-connect-gate").classList.remove("hidden");
  document.querySelector("#meta-report").classList.add("hidden");
  document.querySelector("#meta-connect-button").disabled = false;
  document.querySelector("#meta-connect-button").innerHTML = 'Connect to Meta (demo) <span class="button-arrow">↗</span>';
}

function updateApprovalStatus() {
  const status = document.querySelector("#approval-status");
  const button = document.querySelector("#approval-button");
  const startNewButton = document.querySelector("#start-new-campaign");
  status.classList.toggle("approved", draftApproved);
  status.innerHTML = draftApproved
    ? '<span class="status-dot"></span> Approved · saved locally'
    : editingApprovedDraftId
      ? '<span class="status-dot"></span> Editing approved draft · changes not saved'
      : '<span class="status-dot"></span> Draft · not approved';
  button.textContent = draftApproved
    ? "Revoke approval"
    : editingApprovedDraftId
      ? "Save changes & approve"
      : "Approve draft";
  button.setAttribute("aria-pressed", String(draftApproved));
  startNewButton.classList.toggle("hidden", !draftApproved);
  updateApprovalAvailability();
}

function startNewCampaign() {
  if (!draftApproved) {
    showToast("Approve the current campaign before starting a new one.", true);
    return;
  }
  document.querySelector("#generated-content").classList.add("hidden");
  document.querySelector("#welcome").classList.remove("hidden");
  clearEditVideo();
  document.querySelector("#approval-review-dialog").close();
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.view === "overview");
  });
  document.querySelectorAll(".rail-item").forEach((item) => {
    item.classList.toggle("active", item.dataset.view === "overview");
  });
  currentBrief = null;
  selectedIdea = null;
  selectedLandingCopy = null;
  currentVideoScript = null;
  editingClips = [];
  staticCreativeDirections = [];
  draftApproved = false;
  currentDraftId = null;
  editingApprovedDraftId = null;
  currentCampaignData = null;
  completedCampaignSteps.clear();
  updateApprovalStatus();
  window.scrollTo({ top: 0, behavior: "smooth" });
  showToast("Your approved campaign is saved in Approved drafts. Update the brief to start another.");
}

function markCurrentDraftModified() {
  if (!draftApproved) return;
  editingApprovedDraftId = currentDraftId;
  draftApproved = false;
  updateApprovalStatus();
}

function loadApprovedDraftForEditing(draft) {
  if (!draft.campaign?.brief || !Array.isArray(draft.campaign.ideas)) {
    showToast("This saved draft is missing campaign data and cannot be edited.", true);
    return;
  }
  editingApprovedDraftId = draft.id;
  Object.entries(draft.brief || draft.campaign.brief).forEach(([name, value]) => {
    const field = form.elements.namedItem(name);
    if (field && "value" in field) field.value = value;
  });
  renderCampaign(draft.campaign);
  const savedIdea = draft.idea && draft.campaign.ideas.find((idea) => idea.title === draft.idea.title);
  if (savedIdea) {
    const ideaIndex = draft.campaign.ideas.indexOf(savedIdea);
    const ideaRadio = document.querySelector(`#ideas-list input[value="${ideaIndex}"]`);
    if (ideaRadio) {
      ideaRadio.checked = true;
      ideaRadio.dispatchEvent(new Event("change", { bubbles: true }));
    }
    selectedIdea = savedIdea;
  }
  if (draft.adCopy) updateLandingAdCopy(draft.adCopy);
  if (Array.isArray(draft.script) && draft.script.length) {
    renderVideoScript(draft.script, draft.script[draft.script.length - 1].end_seconds, "Saved approved draft");
  }
  completedCampaignSteps = new Set(
    Array.isArray(draft.completedSteps)
      ? draft.completedSteps.filter((step) => requiredCampaignSteps.some(([key]) => key === step))
      : [],
  );
  updateApprovalAvailability();
  approvedDraftDialog.close();
  showView(savedIdea ? "ideas" : "overview");
  document.querySelector("#generated-content").scrollIntoView({ behavior: "smooth", block: "start" });
  updateApprovalStatus();
  showToast("Draft opened for editing. The approved archive copy stays unchanged until you save and approve.");
}

function toggleDraftApproval() {
  const nextApproved = !draftApproved;
  const briefChanged = Object.entries(currentBrief || {}).some(([name, value]) => {
    const field = form.elements.namedItem(name);
    return field && field.value !== value;
  });
  const missingSteps = requiredCampaignSteps.filter(([step]) => !completedCampaignSteps.has(step));
  if (nextApproved && (missingSteps.length > 0 || briefChanged)) {
    showToast(briefChanged
      ? "Regenerate the campaign after changing its brief before approving."
      : "Complete all required campaign-building steps before approving.", true);
    return;
  }
  const nextDrafts = nextApproved
    ? [...approvedDrafts.filter((draft) => draft.id !== currentDraftId), {
      id: currentDraftId,
      approvedAt: new Date().toISOString(),
      title: document.querySelector("#result-title").textContent,
      brand: currentBrief.brand,
      summary: currentCampaignData.summary,
      brief: currentBrief,
      campaign: currentCampaignData,
      idea: selectedIdea,
      adCopy: selectedLandingCopy,
      script: currentVideoScript,
      completedSteps: [...completedCampaignSteps],
    }]
    : approvedDrafts.filter((draft) => draft.id !== currentDraftId);
  if (!saveApprovedDrafts(nextDrafts)) return;
  draftApproved = nextApproved;
  if (nextApproved) editingApprovedDraftId = null;
  updateApprovalStatus();
  showToast(draftApproved
    ? "Draft approved and saved to this browser. Nothing was published."
    : "Draft approval revoked and removed from the approved drafts archive.");
}

function revealMetaDemoData() {
  document.querySelector("#meta-connect-gate").classList.add("hidden");
  document.querySelector("#meta-report").classList.remove("hidden");
  document.querySelector("#meta-connect-button").disabled = true;
  document.querySelector("#meta-connect-button").textContent = "Demo data loaded";
  showToast("Showing sample campaign data only; no Meta account was connected.");
}

async function downloadLandingPage() {
  if (!currentBrief) {
    showToast("Generate a campaign draft before downloading its landing page.", true);
    return;
  }
  const button = document.querySelector("#download-landing-button");
  button.disabled = true;
  button.textContent = "Preparing standalone page…";
  try {
    const response = await fetch("/api/export-landing-page", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        brief: currentBrief,
        ad_copy: selectedLandingCopy,
      }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || "Could not export the landing page.");
    }

    const file = await response.blob();
    const disposition = response.headers.get("Content-Disposition") || "";
    const filename = disposition.match(/filename="?([^";]+)"?/i)?.[1] || "campaign-landing-page.html";
    const objectUrl = URL.createObjectURL(file);
    const link = document.createElement("a");
    link.href = objectUrl;
    link.download = filename;
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(objectUrl), 1000);
    showToast("Standalone HTML downloaded. Review its content and button links before publishing.");
  } catch (error) {
    showToast(error.message || "Could not export the landing page.", true);
  } finally {
    button.disabled = false;
    button.innerHTML = 'Download landing page <span class="button-arrow">↓</span>';
  }
}

async function generateImagePrompt() {
  if (!currentBrief || staticCreativeDirections.length === 0) {
    showToast("Generate campaign ideas first to create an image prompt.", true);
    return;
  }
  const button = document.querySelector("#generate-image-prompt-button");
  const selectedDirection = staticCreativeDirections[Number(
    document.querySelector("#image-direction-select").value,
  )];
  if (!selectedDirection) {
    showToast("Choose a static image direction first.", true);
    return;
  }

  setCampaignStepComplete("creative", false);
  button.disabled = true;
  button.textContent = "Building image prompt…";
  try {
    const response = await fetch("/api/generate-image-prompt", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        brief: currentBrief,
        creative_direction: selectedDirection,
        aspect_ratio: document.querySelector("#image-aspect-ratio").value,
        idea: selectedIdea,
      }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Could not build the image prompt.");
    document.querySelector("#image-prompt-text").value = data.prompt;
    document.querySelector("#image-prompt-source").textContent =
      `${data.source} · ${data.aspect_ratio}`;
    document.querySelector("#image-prompt-result").classList.remove("hidden");
    setCampaignStepComplete("creative", Boolean(data.prompt.trim()));
    showToast("Image prompt is ready. Copy it into your preferred image model.");
  } catch (error) {
    showToast(error.message || "Could not build the image prompt.", true);
  } finally {
    button.disabled = false;
    button.innerHTML = 'Build image prompt <span class="brand-chip brand-chip-outline">CB</span>';
  }
}

async function copyImagePrompt() {
  const prompt = document.querySelector("#image-prompt-text").value;
  if (!prompt) {
    showToast("Build an image prompt first.", true);
    return;
  }
  try {
    await navigator.clipboard.writeText(prompt);
    showToast("Image prompt copied. Paste it into your image-generation model.");
  } catch {
    showToast("Could not access the clipboard. Select and copy the prompt text manually.", true);
  }
}

async function generateUgcPrompt() {
  if (!currentBrief) {
    showToast("Generate campaign ideas first.", true);
    return;
  }
  const button = document.querySelector("#generate-ugc-prompt-button");
  setCampaignStepComplete("ugc", false);
  button.disabled = true;
  button.textContent = "Building UGC prompt…";
  try {
    const response = await fetch("/api/generate-ugc-prompt", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        brief: currentBrief,
        format: document.querySelector("#ugc-format").value,
        aspect_ratio: document.querySelector("#ugc-aspect-ratio").value,
        idea: selectedIdea,
      }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Could not build the UGC prompt.");
    document.querySelector("#ugc-prompt-text").value = data.prompt;
    document.querySelector("#ugc-prompt-source").textContent = `${data.source} · ${data.aspect_ratio}`;
    document.querySelector("#ugc-prompt-result").classList.remove("hidden");
    setCampaignStepComplete("ugc", Boolean(data.prompt.trim()));
    showToast("UGC prompt is ready to copy into a video model or creator brief.");
  } catch (error) {
    showToast(error.message || "Could not build the UGC prompt.", true);
  } finally {
    button.disabled = false;
    button.innerHTML = 'Build UGC prompt <span class="button-arrow">↗</span>';
  }
}

async function copyUgcPrompt() {
  const prompt = document.querySelector("#ugc-prompt-text").value;
  if (!prompt) {
    showToast("Build a UGC prompt first.", true);
    return;
  }
  try {
    await navigator.clipboard.writeText(prompt);
    showToast("UGC prompt copied.");
  } catch {
    showToast("Could not access the clipboard. Select and copy the prompt text manually.", true);
  }
}

async function generateCampaign(event) {
  event?.preventDefault();
  const submitButton = form.querySelector('button[type="submit"]');
  const activeButton = event?.currentTarget?.tagName === "BUTTON" ? event.currentTarget : submitButton;
  const originalText = activeButton.innerHTML;
  const generationStatus = document.querySelector("#campaign-generation-status");
  activeButton.disabled = true;
  activeButton.textContent = "Generating campaign ideas…";
  generationStatus.textContent = "Generating five strategic concepts. This may take a little while.";

  try {
    const brief = Object.fromEntries(new FormData(form).entries());
    const response = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(brief),
    });
    const data = await response.json().catch(() => null);
    if (!data || typeof data !== "object") {
      throw new Error("The server returned an unreadable response. Restart the app and try again.");
    }
    if (!response.ok) throw new Error(data.error || "Campaign generation failed.");
    renderCampaign(data);
    generationStatus.textContent = `Five ideas are ready · ${data.ideas_source}.`;
    showToast("Ideas are ready. Select one to generate its ad copy.");
  } catch (error) {
    generationStatus.textContent = `Could not generate campaign ideas: ${error.message || "try again."}`;
    showToast(error.message || "Could not generate the campaign.", true);
  } finally {
    activeButton.disabled = false;
    activeButton.innerHTML = originalText;
  }
}

function clearEditSuggestions() {
  editSuggestionsList.replaceChildren();
  editSuggestionsPanel.classList.add("hidden");
}

function renderEditSuggestions(suggestions) {
  clearEditSuggestions();
  if (!Array.isArray(suggestions) || suggestions.length === 0) return;
  suggestions.forEach(({ focus, suggestion }) => {
    const card = document.createElement("article");
    card.className = "edit-suggestion";
    const label = document.createElement("strong");
    label.textContent = focus;
    const detail = document.createElement("p");
    detail.textContent = suggestion;
    card.append(label, detail);
    editSuggestionsList.append(card);
  });
  editSuggestionsPanel.classList.remove("hidden");
}

async function generateSelectedIdeaCopy() {
  if (!currentBrief || !selectedIdea) {
    showToast("Select one campaign idea first.", true);
    return;
  }

  const button = document.querySelector('[data-panel="ideas"] .workflow-next');
  const progress = document.querySelector("#copy-progress");
  const results = document.querySelector("#copy-results");
  const progressMessage = document.querySelector("#progress-message");
  const messages = [
    "Reading the idea you selected…",
    "Writing hooks and headlines for that direction…",
    "Checking the draft against your brief…",
  ];
  clearCampaignStepsAfter("ideas");
  updateLandingAdCopy(null);
  let messageIndex = 0;
  button.disabled = true;
  button.textContent = "Generating ad copy…";
  results.classList.add("hidden");
  progress.classList.remove("hidden");
  progressMessage.textContent = messages[messageIndex];
  showView("copy");
  document.querySelector("#generated-content").scrollIntoView({ behavior: "smooth", block: "start" });
  const messageTimer = setInterval(() => {
    messageIndex = (messageIndex + 1) % messages.length;
    progressMessage.textContent = messages[messageIndex];
  }, 1100);

  try {
    const response = await fetch("/api/generate-copy", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ brief: currentBrief, idea: selectedIdea }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Ad copy generation failed.");

    addOutputCards("hooks-list", data.copy.hooks);
    addOutputCards("headlines-list", data.copy.headlines);
    addOutputCards("primary-list", data.copy.primary_text, "Use on landing page", (body, index) => {
      const headline = data.copy.headlines[index] || data.copy.headlines[0] || data.idea.title;
      const cta = data.copy.cta[0] || currentBrief.cta;
      updateLandingAdCopy({ headline, body, cta, index });
      showToast("Selected ad copy is now included in the landing-page preview and export.");
    });
    addOutputCards("cta-list", data.copy.cta);
    document.querySelector("#copy-angle").textContent = formatSelectedIdea(data.idea);
    document.querySelector("#copy-source").textContent = data.copy_source;
    const firstBody = data.copy.primary_text[0];
    if (firstBody) {
      setCampaignStepComplete("copy");
      updateLandingAdCopy({
        headline: data.copy.headlines[0] || data.idea.title,
        body: firstBody,
        cta: data.copy.cta[0] || currentBrief.cta,
        index: 0,
      });
    }
    progress.classList.add("hidden");
    results.classList.remove("hidden");
    showView("copy");
    updateWorkflowNavigation("copy");
    showToast("Ad copy is ready for your review.");
  } catch (error) {
    progress.classList.add("hidden");
    showToast(error.message || "Could not generate ad copy.", true);
  } finally {
    clearInterval(messageTimer);
    updateWorkflowNavigation("ideas");
  }
}

async function generateVideoScript() {
  if (!currentBrief) {
    showToast("Generate campaign ideas first.", true);
    return;
  }
  const button = document.querySelector("#generate-video-button");
  const progress = document.querySelector("#video-progress");
  const progressMessage = document.querySelector("#video-progress-message");
  const scriptList = document.querySelector("#script-list");
  const durationSeconds = Number(document.querySelector("#video-duration").value);
  const instructions = document.querySelector("#script-improvement").value.trim();
  const isRegenerating = Boolean(currentVideoScript);
  setCampaignStepComplete("script", false);
  setCampaignStepComplete("editing", false);
  currentVideoScript = null;
  editingClips = [];
  stopEditPreview();
  document.querySelector("#edit-timeline").replaceChildren();
  document.querySelector("#edit-timeline-source").textContent =
    "Script updated. Generate a new plan to use the current script context.";
  editAnalysisSummary.textContent = "";
  editAnalysisSummary.classList.add("hidden");
  clearEditSuggestions();
  updateEditPreviewState();
  button.disabled = true;
  button.textContent = isRegenerating ? "Regenerating video script…" : "Generating video script…";
  progress.classList.remove("hidden");
  progressMessage.textContent = selectedIdea
    ? `Adapting “${selectedIdea.title}” to ${durationSeconds} seconds…`
    : `Planning scenes for a ${durationSeconds}-second video…`;
  showView("script");
  const messageTimer = setTimeout(() => {
    progressMessage.textContent = "Pacing the scene timings and checking the total duration…";
  }, 1100);

  try {
    const response = await fetch("/api/generate-video", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        brief: currentBrief,
        duration_seconds: durationSeconds,
        idea: selectedIdea,
        instructions,
      }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Video script generation failed.");
    renderVideoScript(data.script, data.duration_seconds, data.script_source);
    showToast(`${data.duration_seconds}-second video script is ready for review.`);
  } catch (error) {
    showToast(error.message || "Could not generate the video script.", true);
  } finally {
    clearTimeout(messageTimer);
    progress.classList.add("hidden");
    button.disabled = false;
    button.innerHTML = 'Generate / regenerate script <span class="button-arrow">↗</span>';
  }
}

function renderEditTimeline(clips) {
  stopEditPreview();
  editingClips = clips;
  const container = document.querySelector("#edit-timeline");
  container.replaceChildren();
  clips.forEach((clip, index) => {
    const card = document.createElement("article");
    card.className = "edit-clip";
    const heading = document.createElement("div");
    heading.className = "edit-clip-heading";
    const time = document.createElement("strong");
    time.textContent = `CLIP ${String(index + 1).padStart(2, "0")} · ${clip.start_seconds}–${clip.end_seconds}s`;
    const split = document.createElement("button");
    split.type = "button";
    split.className = "button button-outline";
    split.textContent = "Split at midpoint";
    split.disabled = clip.end_seconds - clip.start_seconds < 2;
    split.addEventListener("click", () => splitEditClip(index));
    const actions = document.createElement("div");
    actions.className = "edit-clip-actions";
    const preview = document.createElement("button");
    preview.type = "button";
    preview.className = "button button-outline edit-preview-clip";
    preview.textContent = "Preview cut";
    preview.disabled = !canPreviewEditClip(clip);
    preview.addEventListener("click", () => playEditPreview(index, false));
    actions.append(preview, split);
    heading.append(time, actions);
    const beat = document.createElement("p");
    beat.className = "edit-clip-beat";
    beat.textContent = clip.beat;
    const detail = document.createElement("p");
    detail.textContent = `Visual: ${clip.visual}`;
    card.append(heading, beat, detail);
    if (clip.voiceover) {
      const voiceover = document.createElement("p");
      voiceover.textContent = `Voiceover: ${clip.voiceover}`;
      card.append(voiceover);
    }
    if (clip.on_screen_text) {
      const onscreen = document.createElement("p");
      onscreen.textContent = `On-screen text: ${clip.on_screen_text}`;
      card.append(onscreen);
    }
    const cut = document.createElement("p");
    cut.className = "edit-cut-note";
    cut.textContent = clip.cut_note;
    card.append(cut);
    if (clip.editor_note) {
      const note = document.createElement("p");
      note.className = "edit-cut-note";
      note.textContent = `Editor instruction: ${clip.editor_note}`;
      card.append(note);
    }
    container.append(card);
  });
  updateEditPreviewState();
}

function splitEditClip(index) {
  const clip = editingClips[index];
  if (!clip || clip.end_seconds - clip.start_seconds < 2) {
    showToast("This clip is too short to split further.", true);
    return;
  }
  stopEditPreview();
  const midpoint = clip.start_seconds + Math.floor((clip.end_seconds - clip.start_seconds) / 2);
  const first = { ...clip, end_seconds: midpoint, cut_note: "Cut on action or a natural visual change." };
  const second = {
    ...clip,
    start_seconds: midpoint,
    voiceover: "",
    on_screen_text: "",
    cut_note: clip.cut_note,
  };
  editingClips.splice(index, 1, first, second);
  renderEditTimeline(editingClips);
  document.querySelector("#edit-timeline-source").textContent =
    `Edited locally · ${editingClips.length} clips · ${currentVideoScript[currentVideoScript.length - 1].end_seconds}-second total.`;
}

function formatEditDuration(seconds) {
  const wholeSeconds = Math.round(seconds);
  return `${Math.floor(wholeSeconds / 60)}:${String(wholeSeconds % 60).padStart(2, "0")}`;
}

function stopEditPreview() {
  previewEditSequence = false;
  activePreviewClipIndex = -1;
  editVideoPreview.pause();
  document.querySelector("#edit-preview-caption").textContent = "";
  document.querySelector("#edit-preview-brand").classList.remove("is-visible");
  document.querySelector("#edit-preview-caption").classList.remove("is-visible");
}

function canPreviewEditClip(clip) {
  return Boolean(editVideoObjectUrl && editVideoDuration !== null && editVideoDuration + 0.25 >= clip.end_seconds);
}

function updateEditPreviewState() {
  const editDuration = editingClips.at(-1)?.end_seconds;
  const fullEditFits = Boolean(
    editingClips.length &&
    editVideoDuration !== null &&
    editDuration &&
    editVideoDuration + 0.25 >= editDuration
  );
  buildEditButton.disabled = !editVideoObjectUrl || editVideoDuration === null || editVideoLoadError;
  previewEditButton.disabled = !fullEditFits;
  document.querySelectorAll(".edit-preview-clip").forEach((button, index) => {
    button.disabled = !canPreviewEditClip(editingClips[index]);
  });

  if (editVideoLoadError) {
    editVideoSourceStatus.textContent = editVideoErrorMessage;
  } else if (!editVideoObjectUrl) {
    editVideoSourceStatus.textContent =
      "Choose a video up to 100 MB and 3 minutes. Its duration and three sampled still frames are sent to the configured AI when you generate a plan; the full video stays in this browser.";
  } else if (editVideoDuration === null) {
    editVideoSourceStatus.textContent = "Video selected · reading its duration…";
  } else {
    editVideoSourceStatus.textContent =
      `Source ready · ${editVideoDuration.toFixed(1)} seconds. The full video stays local; three sampled frames are sent for AI analysis when you generate a plan.`;
  }
}

function clearEditVideo() {
  stopEditPreview();
  if (editVideoObjectUrl) URL.revokeObjectURL(editVideoObjectUrl);
  editVideoObjectUrl = null;
  editVideoDuration = null;
  editVideoLoadError = false;
  editVideoErrorMessage = "";
  editVideoUpload.value = "";
  editVideoPreview.removeAttribute("src");
  editVideoPreview.load();
  editVideoStage.classList.add("hidden");
  editingClips = [];
  document.querySelector("#edit-timeline").replaceChildren();
  document.querySelector("#edit-timeline-source").textContent = "Choose a video to enable frame analysis and edit suggestions.";
  editAnalysisSummary.textContent = "";
  editAnalysisSummary.classList.add("hidden");
  clearEditSuggestions();
  updateEditPreviewState();
}

function showEditPreviewClip(index) {
  const clip = editingClips[index];
  if (!clip) return;
  document.querySelector("#edit-preview-brand").textContent = currentBrief?.brand || "";
  document.querySelector("#edit-preview-brand").classList.toggle("is-visible", Boolean(currentBrief?.brand));
  const caption = document.querySelector("#edit-preview-caption");
  caption.textContent = clip.on_screen_text || "";
  caption.classList.toggle("is-visible", Boolean(clip.on_screen_text));
}

async function playEditPreview(index, sequence) {
  const clip = editingClips[index];
  if (!editVideoObjectUrl || editVideoDuration === null || !clip) {
    showToast("Choose a video and generate an edit plan before previewing cuts.", true);
    return;
  }
  if (!canPreviewEditClip(clip)) {
    showToast("This cut extends beyond the uploaded video's duration.", true);
    return;
  }

  editVideoPreview.pause();
  previewEditSequence = sequence;
  activePreviewClipIndex = index;
  showEditPreviewClip(index);
  editVideoPreview.currentTime = clip.start_seconds;
  try {
    await editVideoPreview.play();
  } catch (error) {
    stopEditPreview();
    showToast(`Could not play this video in the browser: ${error.message}`, true);
  }
}

function advanceEditPreview() {
  if (activePreviewClipIndex < 0) return;
  const clip = editingClips[activePreviewClipIndex];
  if (!clip || editVideoPreview.currentTime + 0.05 < clip.end_seconds) return;
  if (previewEditSequence && activePreviewClipIndex < editingClips.length - 1) {
    activePreviewClipIndex += 1;
    const nextClip = editingClips[activePreviewClipIndex];
    showEditPreviewClip(activePreviewClipIndex);
    editVideoPreview.currentTime = nextClip.start_seconds;
    editVideoPreview.play().catch((error) => {
      stopEditPreview();
      showToast(`Could not continue the edit preview: ${error.message}`, true);
    });
    return;
  }
  stopEditPreview();
}

function handleEditVideoUpload() {
  const file = editVideoUpload.files?.[0];
  if (!file) return;
  stopEditPreview();
  if (editVideoObjectUrl) URL.revokeObjectURL(editVideoObjectUrl);
  editVideoObjectUrl = null;
  editVideoDuration = null;
  editVideoLoadError = false;
  editVideoErrorMessage = "";
  editVideoPreview.removeAttribute("src");
  editVideoPreview.load();
  editVideoStage.classList.add("hidden");
  editingClips = [];
  document.querySelector("#edit-timeline").replaceChildren();
  document.querySelector("#edit-timeline-source").textContent = "Choose a video to enable frame analysis and edit suggestions.";
  editAnalysisSummary.textContent = "";
  editAnalysisSummary.classList.add("hidden");
  clearEditSuggestions();
  setCampaignStepComplete("editing", false);
  if (file.type && !file.type.startsWith("video/")) {
    editVideoUpload.value = "";
    editVideoLoadError = true;
    editVideoErrorMessage = "Choose a supported video file to generate an edit plan.";
    updateEditPreviewState();
    showToast("Choose a video file to preview.", true);
    return;
  }
  if (file.size > MAX_EDIT_VIDEO_BYTES) {
    editVideoUpload.value = "";
    editVideoLoadError = true;
    editVideoErrorMessage = "The selected video is larger than the 100 MB limit.";
    updateEditPreviewState();
    showToast(editVideoErrorMessage, true);
    return;
  }
  editVideoObjectUrl = URL.createObjectURL(file);
  editVideoStage.classList.remove("hidden");
  editVideoPreview.src = editVideoObjectUrl;
  editVideoPreview.load();
  editVideoSourceStatus.textContent = `${file.name} selected · reading its duration…`;
  updateEditPreviewState();
}

function seekEditVideoTo(seconds) {
  return new Promise((resolve, reject) => {
    const video = editVideoPreview;
    const timeout = setTimeout(() => {
      video.removeEventListener("seeked", onSeeked);
      reject(new Error("Timed out while extracting a frame from the video."));
    }, 5000);
    const onSeeked = () => {
      clearTimeout(timeout);
      resolve();
    };
    video.addEventListener("seeked", onSeeked, { once: true });
    try {
      video.currentTime = seconds;
      if (Math.abs(video.currentTime - seconds) < 0.001 && !video.seeking) {
        video.removeEventListener("seeked", onSeeked);
        clearTimeout(timeout);
        resolve();
      }
    } catch (error) {
      video.removeEventListener("seeked", onSeeked);
      clearTimeout(timeout);
      reject(new Error(`Could not seek to a video frame: ${error.message}`));
    }
  });
}

async function extractThreeEditFrames() {
  if (!editVideoObjectUrl || editVideoDuration === null || editVideoLoadError) {
    throw new Error("Choose a valid video before generating the edit plan.");
  }
  const video = editVideoPreview;
  const previousTime = video.currentTime;
  const scale = Math.min(1, 512 / Math.max(video.videoWidth, video.videoHeight));
  const canvas = document.createElement("canvas");
  canvas.width = Math.max(1, Math.round(video.videoWidth * scale));
  canvas.height = Math.max(1, Math.round(video.videoHeight * scale));
  const context = canvas.getContext("2d");
  if (!context) throw new Error("This browser cannot extract video frames.");

  const timestamps = [editVideoDuration * 0.1, editVideoDuration * 0.5, editVideoDuration * 0.9];
  const frames = [];
  video.pause();
  try {
    for (const timestamp of timestamps) {
      await seekEditVideoTo(timestamp);
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      const image = canvas.toDataURL("image/jpeg", 0.72);
      if (image.length > 700000) {
        throw new Error("A sampled frame is too large to send. Choose a lower-resolution video.");
      }
      frames.push({ timestamp_seconds: Number(timestamp.toFixed(3)), image });
    }
  } finally {
    await seekEditVideoTo(Math.min(previousTime, Math.max(0, editVideoDuration - 0.01)));
  }
  return frames;
}

async function buildEditTimeline() {
  if (!editVideoObjectUrl || editVideoDuration === null || editVideoLoadError) {
    editVideoUpload.focus();
    showToast("Choose and load a video before generating its edit plan.", true);
    return;
  }
  setCampaignStepComplete("editing", false);
  editingClips = [];
  document.querySelector("#edit-timeline").replaceChildren();
  document.querySelector("#edit-timeline-source").textContent = "Analyzing the video duration and sampled frames…";
  buildEditButton.disabled = true;
  buildEditButton.textContent = "Analyzing video…";
  editAnalysisSummary.textContent = "";
  editAnalysisSummary.classList.add("hidden");
  clearEditSuggestions();
  updateEditPreviewState();
  try {
    editVideoSourceStatus.textContent = "Extracting three video frames locally…";
    const frames = await extractThreeEditFrames();
    const response = await fetch("/api/analyze-edit-video", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        duration_seconds: editVideoDuration,
        frames,
        script: currentVideoScript,
        split_interval_seconds: Number(document.querySelector("#edit-split-interval").value),
        instructions: document.querySelector("#editing-instructions").value.trim(),
      }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Could not build the editing timeline.");
    renderEditSuggestions(data.edit_suggestions);
    renderEditTimeline(data.clips);
    setCampaignStepComplete("editing", data.clips.length > 0);
    document.querySelector("#edit-timeline-source").textContent =
      `${data.source} · 3 sampled frames · ${Number(data.duration_seconds).toFixed(1)} seconds · ${data.clip_count} clips.`;
    editAnalysisSummary.textContent = data.analysis_summary;
    editAnalysisSummary.classList.remove("hidden");
    showToast("Edit timeline is ready. Split any clip again at its midpoint.");
  } catch (error) {
    showToast(error.message || "Could not build the editing timeline.", true);
  } finally {
    buildEditButton.innerHTML = 'Generate edit plan <span class="button-arrow">↗</span>';
    updateEditPreviewState();
  }
}

async function generateMediaPlan() {
  if (!currentBrief) {
    showToast("Generate campaign ideas first.", true);
    return;
  }
  const button = document.querySelector("#generate-media-plan");
  const budget = Number(document.querySelector("#media-daily-budget").value);
  setCampaignStepComplete("media", false);
  button.disabled = true;
  button.textContent = "Building plan…";
  try {
    const response = await fetch("/api/media-plan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ brief: currentBrief, daily_budget: budget, idea: selectedIdea }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Could not build the media plan.");
    document.querySelector("#media-plan-source").textContent =
      `${data.source} · based on this brief${selectedIdea ? ` and “${selectedIdea.title}”` : ""} · no live ad account`;
    document.querySelector("#media-plan-kpi").textContent = data.primary_kpi;
    const allocations = data.allocations.map((item) =>
      `${item.name}: $${item.daily_budget.toFixed(2)}/day (${item.share_percent}%) · optimize for ${item.success_metric}`);
    addOutputCards("media-plan-allocations", allocations);
    addOutputCards("media-plan-actions", data.actions);
    addOutputCards("media-plan-guardrails", data.guardrails);
    document.querySelector("#media-plan-result").classList.remove("hidden");
    setCampaignStepComplete("media");
    showToast("Brief-based planning recommendations are ready for review.");
  } catch (error) {
    showToast(error.message || "Could not build the media plan.", true);
  } finally {
    button.disabled = false;
    button.innerHTML = 'Build media plan <span class="button-arrow">↗</span>';
  }
}

form.addEventListener("submit", generateCampaign);
document.querySelector("#generate-video-button").addEventListener("click", generateVideoScript);
const approvalReviewDialog = document.querySelector("#approval-review-dialog");
document.querySelector("#approval-button").addEventListener("click", () => {
  if (draftApproved) {
    toggleDraftApproval();
    return;
  }
  updateApprovalAvailability();
  approvalReviewDialog.showModal();
});
document.querySelector("#start-new-campaign").addEventListener("click", startNewCampaign);
document.querySelector("#confirm-approval-button").addEventListener("click", () => {
  toggleDraftApproval();
  if (draftApproved) approvalReviewDialog.close();
});
document.querySelector("#close-approval-review").addEventListener("click", () => approvalReviewDialog.close());
document.querySelector("#meta-connect-button").addEventListener("click", revealMetaDemoData);
document.querySelector("#download-landing-button").addEventListener("click", downloadLandingPage);
document.querySelector("#generate-image-prompt-button").addEventListener("click", generateImagePrompt);
document.querySelector("#copy-image-prompt-button").addEventListener("click", copyImagePrompt);
document.querySelector("#generate-ugc-prompt-button").addEventListener("click", generateUgcPrompt);
document.querySelector("#copy-ugc-prompt-button").addEventListener("click", copyUgcPrompt);
document.querySelector("#build-edit-timeline").addEventListener("click", buildEditTimeline);
previewEditButton.addEventListener("click", () => playEditPreview(0, true));
editVideoUpload.addEventListener("change", handleEditVideoUpload);
editVideoPreview.addEventListener("loadedmetadata", () => {
  const duration = editVideoPreview.duration;
  if (!Number.isFinite(duration) || duration < 0.5) {
    editVideoLoadError = true;
    editVideoErrorMessage = "Choose a video at least 0.5 seconds long.";
    editVideoDuration = null;
  } else if (duration > MAX_EDIT_VIDEO_DURATION_SECONDS) {
    editVideoLoadError = true;
    editVideoErrorMessage = "Videos must be 3 minutes or shorter for edit planning.";
    editVideoDuration = null;
  } else {
    editVideoLoadError = false;
    editVideoErrorMessage = "";
    editVideoDuration = duration;
  }
  updateEditPreviewState();
});
editVideoPreview.addEventListener("error", () => {
  if (!editVideoObjectUrl) return;
  editVideoDuration = null;
  editVideoLoadError = true;
  editVideoErrorMessage = "This browser could not play the selected video. Try an MP4 or WebM file.";
  updateEditPreviewState();
  showToast(editVideoErrorMessage, true);
});
editVideoPreview.addEventListener("timeupdate", advanceEditPreview);
editVideoPreview.addEventListener("ended", advanceEditPreview);
document.querySelector("#generate-media-plan").addEventListener("click", generateMediaPlan);
form.addEventListener("input", () => {
  markCurrentDraftModified();
  updateApprovalAvailability();
});
[
  ["#image-direction-select", "creative", "change"],
  ["#image-aspect-ratio", "creative", "change"],
  ["#script-improvement", "script", "input"],
  ["#video-duration", "script", "change"],
  ["#ugc-format", "ugc", "change"],
  ["#ugc-aspect-ratio", "ugc", "change"],
  ["#edit-split-interval", "editing", "change"],
  ["#editing-instructions", "editing", "input"],
  ["#media-daily-budget", "media", "input"],
].forEach(([selector, step, eventName]) => {
  document.querySelector(selector).addEventListener(eventName, () => {
    setCampaignStepComplete(step, false);
  });
});
const appShell = document.querySelector(".app-shell");
const railToggle = document.querySelector("#rail-toggle");
railToggle.addEventListener("click", () => {
  const expanded = appShell.classList.toggle("sidebar-expanded");
  railToggle.setAttribute("aria-expanded", String(expanded));
  railToggle.setAttribute("aria-label", expanded ? "Collapse sidebar" : "Expand sidebar");
  railToggle.querySelector(".rail-toggle-label").textContent = expanded ? "Collapse menu" : "Expand menu";
  railToggle.title = expanded ? "Collapse sidebar" : "Expand sidebar";
});
const approvedDraftDialog = document.querySelector("#approved-drafts-dialog");
function openApprovedDrafts() {
  approvedDraftDialog.showModal();
}
document.querySelector("#open-approved-drafts").addEventListener("click", openApprovedDrafts);
document.querySelector("#open-approved-drafts-nav").addEventListener("click", openApprovedDrafts);
document.querySelector("#close-approved-drafts").addEventListener("click", () => approvedDraftDialog.close());
approvedDraftDialog.addEventListener("click", (event) => {
  if (event.target === approvedDraftDialog) approvedDraftDialog.close();
});
document.querySelectorAll("[data-view]").forEach((button) => {
  button.addEventListener("click", () => {
    if (document.querySelector("#generated-content").classList.contains("hidden")) {
      showToast("Build a campaign first to explore its outputs.");
      return;
    }
    document.querySelector("#generated-content").scrollIntoView({ behavior: "smooth", block: "start" });
    showView(button.dataset.view);
  });
});
setupWorkflowNavigation();
approvedDrafts = loadApprovedDrafts();
renderApprovedDrafts();
updateApprovalAvailability();
