const defaultApiBase = "http://localhost:8080";
const apiBaseInput = document.querySelector("#apiBase");
const runState = document.querySelector("#runState");
const summaryCards = document.querySelector("#summaryCards");
const teacherAlertReport = document.querySelector("#teacherAlertReport");
const supportTopics = document.querySelector("#supportTopics");
const nodeDetails = document.querySelector("#nodeDetails");
const graphLegend = document.querySelector("#graphLegend");

let labelsVisible = true;

const graphState = {
  student: {
    cy: null,
    mode: "student",
    graph: { nodes: [], edges: [] },
    container: document.querySelector("#studentGraphPreview"),
    stats: document.querySelector("#studentGraphStats"),
    subtitle: document.querySelector("#studentGraphSubtitle"),
    emptyIcon: "person_search",
    emptyTitle: "Student graph",
    emptyText: "Draw this graph after entering or loading a student case.",
    defaultSubtitle: "Student-specific target topics, prerequisites, and missing-topic statuses.",
  },
  curriculum: {
    cy: null,
    mode: "curriculum",
    graph: { nodes: [], edges: [] },
    container: document.querySelector("#curriculumGraphPreview"),
    stats: document.querySelector("#curriculumGraphStats"),
    subtitle: document.querySelector("#curriculumGraphSubtitle"),
    emptyIcon: "menu_book",
    emptyTitle: "Curriculum graph",
    emptyText: "Draw the original curriculum graph to compare it with the student graph.",
    defaultSubtitle: "Original curriculum slice for visual comparison.",
  },
};

const statusStyles = {
  target: {
    label: "Target topic",
    color: "#fed65b",
    border: "#735c00",
    text: "#241a00",
  },
  likely_missed_due_to_switch: {
    label: "Likely missed prerequisite",
    color: "#ffdad6",
    border: "#ba1a1a",
    text: "#650006",
  },
  likely_covered_abroad: {
    label: "Likely covered abroad",
    color: "#d7f5df",
    border: "#1b7f3a",
    text: "#0b4d23",
  },
  bridge_available_outside_student_path: {
    label: "Bridge outside studied path",
    color: "#d2e4fb",
    border: "#4f6073",
    text: "#0b1d2d",
  },
  currently_in_target_grade_path: {
    label: "Current target-grade path",
    color: "#e1e3e4",
    border: "#74777d",
    text: "#191c1d",
  },
  curriculum: {
    label: "Curriculum topic",
    color: "#efe5ff",
    border: "#7b4fb3",
    text: "#2d174f",
  },
  default: {
    label: "Topic",
    color: "#f8f9fa",
    border: "#74777d",
    text: "#191c1d",
  },
};

apiBaseInput.value = localStorage.getItem("gapDetectionApiBase") || defaultApiBase;

function apiUrl(path) {
  return `${apiBaseInput.value.replace(/\/$/, "")}${path}`;
}

function setState(label) {
  runState.textContent = label;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function getStatusStyle(status) {
  return statusStyles[status] || statusStyles.default;
}

function truncateLabel(value, limit = 34) {
  const text = String(value || "");
  return text.length > limit ? `${text.slice(0, limit - 1)}...` : text;
}

function getCasePayload() {
  const form = new FormData(document.querySelector("#studentCaseForm"));
  const gradesText = String(form.get("grades_studied_abroad") || "");
  const numberOrNull = (value) => {
    if (value === null || value === "") return null;
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  };

  return {
    case_id: form.get("case_id") || null,
    origin_country: form.get("origin_country") || "Turkey",
    grades_studied_abroad: gradesText.split(",").map((item) => item.trim()).filter(Boolean),
    last_completed_grade_abroad: form.get("last_completed_grade_abroad") || null,
    target_country: form.get("target_country") || "Syria",
    target_grade: form.get("target_grade") || "12",
    target_stream: form.get("target_stream") || "Scientific",
    subject_focus: form.get("subject_focus") || "Math",
    overall_difficulty: numberOrNull(form.get("overall_difficulty")),
    math_difficulty: numberOrNull(form.get("math_difficulty")),
    notes: form.get("notes") || null,
  };
}

function getCurriculumPayload() {
  return {
    country: document.querySelector("#graphCountry").value || "Syria",
    grade: document.querySelector("#graphGrade").value || "12",
    stream: document.querySelector("#graphStream").value || "Scientific",
    subject: document.querySelector("#graphSubject").value || "Math",
    core_only: true,
  };
}

async function postJson(path, payload) {
  const response = await fetch(apiUrl(path), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with status ${response.status}`);
  }
  return response.json();
}

function renderSummary(summary) {
  const items = [
    ["Target topics", summary.n_target_topics],
    ["Prerequisite links", summary.n_direct_prereq_links],
    ["Support topics", summary.n_support_topics],
    ["Likely missed", summary.n_likely_missed_topics],
    ["Covered abroad", summary.n_likely_covered_abroad_topics],
    ["Outside-path bridges", summary.n_bridge_topics_outside_path],
  ];
  summaryCards.innerHTML = items
    .map(
      ([label, value]) =>
        `<div class="summary-card"><span>${escapeHtml(label)}</span><strong>${escapeHtml(value ?? "--")}</strong></div>`,
    )
    .join("");
}

function renderTeacherAlert(rows) {
  if (!rows.length) {
    teacherAlertReport.innerHTML = '<p class="text-sm text-slate-600">No likely missed prerequisites returned yet.</p>';
    return;
  }

  teacherAlertReport.innerHTML = `
    <table class="table">
      <thead>
        <tr>
          <th>Target topic</th>
          <th>Prerequisite</th>
          <th>Relation</th>
          <th>Grade</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        ${rows
          .map(
            (row) => `
              <tr>
                <td>${escapeHtml(row.target_topic_name_en)}</td>
                <td>${escapeHtml(row.prereq_topic_name_en)}</td>
                <td>${escapeHtml(row.relation_type)} ${row.strength ? `(${escapeHtml(row.strength)})` : ""}</td>
                <td>${escapeHtml(row.prereq_grade)}</td>
                <td>${escapeHtml(row.status_label)}</td>
              </tr>
            `,
          )
          .join("")}
      </tbody>
    </table>
  `;
}

function renderSupportTopics(rows) {
  if (!rows.length) {
    supportTopics.innerHTML = '<p class="text-sm text-slate-600">Support-first topics will appear after analysis.</p>';
    return;
  }

  supportTopics.innerHTML = rows
    .map(
      (row) => `
        <article class="topic-card">
          <div class="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <h4 class="font-semibold text-[#041627]">${escapeHtml(row.prereq_topic_name_en || row.from_topic_id)}</h4>
              <p class="mt-1 text-sm text-slate-600">Supports: ${escapeHtml(row.supported_targets || "Target topics")}</p>
            </div>
            <span class="status-pill">${escapeHtml(row.support_count || 0)} links</span>
          </div>
        </article>
      `,
    )
    .join("");
}

function renderLegend() {
  const statuses = [
    "target",
    "likely_missed_due_to_switch",
    "likely_covered_abroad",
    "bridge_available_outside_student_path",
    "currently_in_target_grade_path",
    "curriculum",
  ];

  graphLegend.innerHTML = statuses
    .map((status) => {
      const style = getStatusStyle(status);
      return `
        <div class="legend-item">
          <span class="legend-swatch" style="background:${style.color}; border-color:${style.border}"></span>
          <span>${escapeHtml(style.label)}</span>
        </div>
      `;
    })
    .join("");
}

function toCytoscapeElements(graph) {
  const nodeIds = new Set((graph.nodes || []).map((node) => String(node.id)));
  const nodes = (graph.nodes || []).map((node) => {
    const style = getStatusStyle(node.status);
    return {
      data: {
        ...node,
        id: String(node.id),
        label: node.label || node.id,
        shortLabel: truncateLabel(node.label || node.id),
        bgColor: style.color,
        borderColor: style.border,
        textColor: style.text,
      },
    };
  });

  const edges = (graph.edges || [])
    .filter((edge) => nodeIds.has(String(edge.source)) && nodeIds.has(String(edge.target)))
    .map((edge, index) => ({
      data: {
        ...edge,
        id: edge.id || `edge-${index}-${edge.source}-${edge.target}`,
        source: String(edge.source),
        target: String(edge.target),
        label: edge.type || "prerequisite",
      },
    }));

  return [...nodes, ...edges];
}

function graphLayout(mode) {
  return {
    name: "cose",
    animate: true,
    animationDuration: 650,
    fit: true,
    padding: 34,
    nodeRepulsion: 9000,
    nodeOverlap: 20,
    idealEdgeLength: mode === "student" ? 108 : 88,
    edgeElasticity: 120,
    gravity: 0.25,
    numIter: 1100,
  };
}

function emptyGraphMarkup(state, title = state.emptyTitle, text = state.emptyText) {
  return `
    <div class="graph-empty-state">
      <span class="material-symbols-outlined">${state.emptyIcon}</span>
      <strong>${escapeHtml(title)}</strong>
      <p>${escapeHtml(text)}</p>
    </div>
  `;
}

function renderGraph(kind, graph) {
  const state = graphState[kind];
  state.graph = graph || { nodes: [], edges: [] };
  state.stats.textContent = `${state.graph.nodes.length} nodes, ${state.graph.edges.length} edges`;

  if (state.cy) {
    state.cy.destroy();
    state.cy = null;
  }

  if (!state.graph.nodes.length) {
    state.container.innerHTML = emptyGraphMarkup(state, "No graph data returned", "Try a different student case or curriculum slice.");
    renderSelectedDetails(null);
    return;
  }

  state.container.innerHTML = "";
  if (typeof cytoscape === "undefined") {
    state.container.innerHTML = emptyGraphMarkup(state, "Graph library not loaded", "Check internet access or bundle Cytoscape locally before the live demo.");
    return;
  }

  state.cy = cytoscape({
    container: state.container,
    elements: toCytoscapeElements(state.graph),
    wheelSensitivity: 0.18,
    minZoom: 0.18,
    maxZoom: 2.6,
    style: [
      {
        selector: "node",
        style: {
          "background-color": "data(bgColor)",
          "border-color": "data(borderColor)",
          "border-width": 3,
          color: "#17202a",
          content: labelsVisible ? "data(shortLabel)" : "",
          "font-size": 9,
          "font-weight": 700,
          "min-zoomed-font-size": 7,
          "text-halign": "center",
          "text-valign": "center",
          "text-wrap": "wrap",
          "text-max-width": 76,
          height: (node) => (node.data("type") === "target_topic" ? 58 : 46),
          width: (node) => (node.data("type") === "target_topic" ? 58 : 46),
          "overlay-opacity": 0,
          "transition-duration": "150ms",
        },
      },
      {
        selector: 'node[status = "likely_missed_due_to_switch"]',
        style: {
          "border-width": 5,
          height: 58,
          width: 58,
        },
      },
      {
        selector: 'node[type = "target_topic"]',
        style: {
          shape: "round-rectangle",
          "border-width": 4,
        },
      },
      {
        selector: "edge",
        style: {
          "curve-style": "bezier",
          "line-color": "#9aa0a6",
          "target-arrow-color": "#9aa0a6",
          "target-arrow-shape": "triangle",
          width: 1.35,
          opacity: 0.72,
          label: labelsVisible ? "data(label)" : "",
          "font-size": 6,
          color: "#6b7280",
          "text-background-color": "#ffffff",
          "text-background-opacity": 0.85,
          "text-background-padding": 2,
          "text-rotation": "autorotate",
        },
      },
      {
        selector: ":selected",
        style: {
          "border-color": "#041627",
          "line-color": "#041627",
          "target-arrow-color": "#041627",
          "border-width": 6,
          opacity: 1,
          "z-index": 999,
        },
      },
      {
        selector: ".faded",
        style: { opacity: 0.18 },
      },
      {
        selector: ".highlighted",
        style: { opacity: 1, "z-index": 999 },
      },
    ],
    layout: graphLayout(state.mode),
  });

  state.cy.on("tap", "node, edge", (event) => {
    focusElement(state, event.target);
    renderSelectedDetails(event.target, kind);
  });

  state.cy.on("tap", (event) => {
    if (event.target === state.cy) {
      state.cy.elements().removeClass("faded highlighted");
      renderSelectedDetails(null);
    }
  });

  state.cy.on("mouseover", "node", (event) => {
    state.subtitle.textContent = event.target.data("label") || "Topic";
  });

  state.cy.on("mouseout", "node", () => {
    state.subtitle.textContent = state.defaultSubtitle;
  });

  renderSelectedDetails(null);
}

function focusElement(state, element) {
  state.cy.elements().addClass("faded").removeClass("highlighted");

  if (element.isNode()) {
    element.closedNeighborhood().removeClass("faded").addClass("highlighted");
  } else {
    element.removeClass("faded").addClass("highlighted");
    element.connectedNodes().removeClass("faded").addClass("highlighted");
  }
}

function renderSelectedDetails(element, graphKind = "") {
  if (!element) {
    nodeDetails.innerHTML = `
      <h3 class="font-serif text-2xl font-bold text-[#041627]">Nothing selected</h3>
      <p class="mt-2 text-sm leading-6 text-slate-600">
        Click a node or edge in either graph to inspect its educational meaning.
      </p>
    `;
    return;
  }

  const data = element.data();
  const graphLabel = graphKind === "student" ? "Student graph" : "Curriculum graph";

  if (element.isEdge()) {
    nodeDetails.innerHTML = `
      <h3 class="font-serif text-2xl font-bold text-[#041627]">Prerequisite Link</h3>
      <p class="mt-1 text-sm text-slate-600">${escapeHtml(graphLabel)}</p>
      <dl class="detail-list">
        <div><dt>From</dt><dd>${escapeHtml(data.source)}</dd></div>
        <div><dt>To</dt><dd>${escapeHtml(data.target)}</dd></div>
        <div><dt>Relation</dt><dd>${escapeHtml(data.type || data.label || "prerequisite")}</dd></div>
        <div><dt>Strength</dt><dd>${escapeHtml(data.strength || "not specified")}</dd></div>
        <div><dt>Status</dt><dd>${escapeHtml(data.status || "curriculum relation")}</dd></div>
      </dl>
    `;
    return;
  }

  const style = getStatusStyle(data.status);
  nodeDetails.innerHTML = `
    <div class="selected-node-header">
      <span class="legend-swatch" style="background:${style.color}; border-color:${style.border}"></span>
      <div>
        <h3 class="font-serif text-2xl font-bold text-[#041627]">${escapeHtml(data.label || data.id)}</h3>
        <p class="mt-1 text-sm text-slate-600">${escapeHtml(graphLabel)} - ${escapeHtml(style.label)}</p>
      </div>
    </div>
    <dl class="detail-list">
      <div><dt>Node ID</dt><dd>${escapeHtml(data.id)}</dd></div>
      <div><dt>Type</dt><dd>${escapeHtml(data.type || "topic")}</dd></div>
      <div><dt>Status</dt><dd>${escapeHtml(data.status || "not specified")}</dd></div>
      <div><dt>Group</dt><dd>${escapeHtml(data.group || "not specified")}</dd></div>
      <div><dt>Connected links</dt><dd>${escapeHtml(element.connectedEdges().length)}</dd></div>
    </dl>
  `;
}

function rerunGraphLayout(kind) {
  const state = graphState[kind];
  if (!state.cy || !state.graph.nodes.length) return;
  state.cy.layout(graphLayout(state.mode)).run();
}

function fitGraph(kind) {
  const state = graphState[kind];
  if (!state.cy || !state.graph.nodes.length) return;
  state.cy.fit(undefined, 40);
}

function setLabelsVisible(visible) {
  labelsVisible = visible;
  Object.values(graphState).forEach((state) => {
    if (!state.cy) return;
    state.cy
      .style()
      .selector("node")
      .style("content", labelsVisible ? "data(shortLabel)" : "")
      .selector("edge")
      .style("label", labelsVisible ? "data(label)" : "")
      .update();
  });
}

async function loadStudentGraph() {
  setState("Loading student graph");
  graphState.student.stats.textContent = "Loading...";
  try {
    const graph = await postJson("/student-graph", getCasePayload());
    renderGraph("student", graph);
    window.location.hash = "knowledge-graph";
    setState("Student graph ready");
  } catch (error) {
    setState("Error");
    graphState.student.stats.textContent = "Error";
    graphState.student.container.innerHTML = `<p class="p-4 text-sm text-red-700">${escapeHtml(error.message)}</p>`;
  }
}

async function loadCurriculumGraph() {
  graphState.curriculum.stats.textContent = "Loading...";
  try {
    const graph = await postJson("/curriculum-graph", getCurriculumPayload());
    renderGraph("curriculum", graph);
    setState("Curriculum graph ready");
  } catch (error) {
    setState("Error");
    graphState.curriculum.stats.textContent = "Error";
    graphState.curriculum.container.innerHTML = `<p class="p-4 text-sm text-red-700">${escapeHtml(error.message)}</p>`;
  }
}

async function loadBothGraphs() {
  setState("Loading comparison graphs");
  await Promise.all([loadStudentGraph(), loadCurriculumGraph()]);
  setState("Comparison ready");
}

document.querySelector("#saveApiBase").addEventListener("click", () => {
  localStorage.setItem("gapDetectionApiBase", apiBaseInput.value);
  document.querySelector("#healthStatus").textContent = "API base URL saved for this browser.";
});

document.querySelector("#checkHealth").addEventListener("click", async () => {
  const status = document.querySelector("#healthStatus");
  status.textContent = "Checking backend...";
  try {
    const response = await fetch(apiUrl("/health"));
    const data = await response.json();
    status.textContent = `Backend status: ${data.status}`;
  } catch (error) {
    status.textContent = `Backend not reachable: ${error.message}`;
  }
});

document.querySelector("#loadDemo").addEventListener("click", () => {
  const form = document.querySelector("#studentCaseForm");
  form.case_id.value = "SC_DEMO_001";
  form.origin_country.value = "Turkey";
  form.grades_studied_abroad.value = "9, 10, 11";
  form.last_completed_grade_abroad.value = "11";
  form.target_country.value = "Syria";
  form.target_grade.value = "12";
  form.target_stream.value = "Scientific";
  form.subject_focus.value = "Math";
  form.overall_difficulty.value = "6";
  form.math_difficulty.value = "7";
  form.notes.value = "Returning student preparing for Syrian scientific stream mathematics.";
});

document.querySelector("#fitStudentGraph").addEventListener("click", () => fitGraph("student"));
document.querySelector("#rerunStudentLayout").addEventListener("click", () => rerunGraphLayout("student"));
document.querySelector("#fitCurriculumGraph").addEventListener("click", () => fitGraph("curriculum"));
document.querySelector("#rerunCurriculumLayout").addEventListener("click", () => rerunGraphLayout("curriculum"));
document.querySelector("#toggleLabels").addEventListener("change", (event) => setLabelsVisible(event.target.checked));

document.querySelector("#studentCaseForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  setState("Running");
  try {
    const data = await postJson("/analyze-student-case", getCasePayload());
    renderSummary(data.summary);
    renderTeacherAlert(data.teacher_alert_report);
    renderSupportTopics(data.support_first_topics);
    setState("Complete");
  } catch (error) {
    setState("Error");
    teacherAlertReport.innerHTML = `<p class="text-sm text-red-700">${escapeHtml(error.message)}</p>`;
  }
});

document.querySelector("#drawStudentGraph").addEventListener("click", loadStudentGraph);
document.querySelector("#loadStudentGraph").addEventListener("click", loadStudentGraph);
document.querySelector("#loadCurriculumGraph").addEventListener("click", loadCurriculumGraph);
document.querySelector("#loadBothGraphs").addEventListener("click", loadBothGraphs);

renderSummary({});
renderTeacherAlert([]);
renderSupportTopics([]);
renderLegend();
