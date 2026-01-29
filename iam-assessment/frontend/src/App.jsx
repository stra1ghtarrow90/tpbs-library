import { useEffect, useMemo, useState } from "react";
import {
  createAssessment,
  getAssessment,
  getAssessments,
  getReport,
  updateItem,
} from "./api";
import "./styles.css";

const STORAGE_KEY = "iamAssessmentId";
const HOME_ROUTE = "/";
const ASSESSOR_ROUTE = "/iam-assessor";
const KNOWLEDGE_ROUTE = "/knowledge-base";

function getRoute() {
  const hash = window.location.hash.replace("#", "");
  if (!hash || hash === "/") return HOME_ROUTE;
  return hash.startsWith("/") ? hash : `/${hash}`;
}

function groupByDomain(items) {
  return items.reduce((acc, item) => {
    acc[item.domain] = acc[item.domain] || [];
    acc[item.domain].push(item);
    return acc;
  }, {});
}

export default function App() {
  const [route, setRoute] = useState(() => getRoute());
  const [assessment, setAssessment] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState("");
  const [report, setReport] = useState(null);

  useEffect(() => {
    function handleHashChange() {
      setRoute(getRoute());
    }
    window.addEventListener("hashchange", handleHashChange);
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  useEffect(() => {
    if (route !== ASSESSOR_ROUTE) return;
    async function init() {
      try {
        setLoading(true);
        const storedId = localStorage.getItem(STORAGE_KEY);
        if (storedId) {
          const data = await getAssessment(storedId);
          setAssessment(data);
          setLoading(false);
          return;
        }

        const existing = await getAssessments();
        if (existing.length > 0) {
          const data = await getAssessment(existing[0].id);
          localStorage.setItem(STORAGE_KEY, existing[0].id);
          setAssessment(data);
          setLoading(false);
          return;
        }

        const created = await createAssessment({ name: "Draft Assessment" });
        localStorage.setItem(STORAGE_KEY, created.id);
        setAssessment(created);
      } catch (err) {
        setError(err.message || "Failed to load assessment");
      } finally {
        setLoading(false);
      }
    }
    init();
  }, [route]);

  const grouped = useMemo(() => {
    if (!assessment) return {};
    const items = [...assessment.items].sort((a, b) =>
      a.control_id.localeCompare(b.control_id)
    );
    return groupByDomain(items);
  }, [assessment]);

  function updateLocal(controlId, field, value) {
    setAssessment((prev) => {
      if (!prev) return prev;
      const items = prev.items.map((item) =>
        item.control_id === controlId ? { ...item, [field]: value } : item
      );
      return { ...prev, items };
    });
  }

  async function handleSave(item) {
    setSaving(item.control_id);
    try {
      const payload = {
        status: item.status,
        score: item.status === "assessed" ? item.score : null,
        finding_text: item.finding_text,
        evidence_refs: item.evidence_refs,
        assessor_notes: item.assessor_notes,
      };
      const updated = await updateItem(assessment.id, item.control_id, payload);
      updateLocal(item.control_id, "status", updated.status);
      updateLocal(item.control_id, "score", updated.score);
      updateLocal(item.control_id, "finding_text", updated.finding_text);
      updateLocal(item.control_id, "evidence_refs", updated.evidence_refs);
      updateLocal(item.control_id, "assessor_notes", updated.assessor_notes);
    } catch (err) {
      setError(err.message || "Failed to save item");
    } finally {
      setSaving("");
    }
  }

  async function handleReport() {
    setError("");
    try {
      const data = await getReport(assessment.id);
      setReport(data);
    } catch (err) {
      setError(err.message || "Failed to build report");
    }
  }

  if (route === KNOWLEDGE_ROUTE) {
    return (
      <div className="page home">
        <div className="nav">
          <a className="ghost-link" href={`#${HOME_ROUTE}`}>
            ← Back to index
          </a>
        </div>
        <section className="kb-hero">
          <div>
            <p className="eyebrow">Knowledge Base</p>
            <h1>Identity Architecture Library</h1>
            <p className="lede">
              Build out frameworks, reference patterns, and remediation guidance
              in a single place.
            </p>
          </div>
          <div className="kb-panel">
            <h2>Coming Soon</h2>
            <p>
              This section will host architecture patterns, control narratives,
              and reusable guidance for IAM and broader security domains.
            </p>
            <a className="primary" href={`#${ASSESSOR_ROUTE}`}>
              Jump to IAM Assessor
            </a>
          </div>
        </section>
        <section className="home-grid">
          <div className="home-panel">
            <h3>Frameworks</h3>
            <p>
              Map IAM controls to business capabilities, technology layers, and
              operating models.
            </p>
          </div>
          <div className="home-panel">
            <h3>Reference Patterns</h3>
            <p>
              Capture proven architectures for workforce, privileged access,
              and cloud identity.
            </p>
          </div>
          <div className="home-panel">
            <h3>Remediation Playbooks</h3>
            <p>
              Record mitigations, owners, and execution guidance tied to the
              IAM assessment results.
            </p>
          </div>
        </section>
      </div>
    );
  }

  if (route !== ASSESSOR_ROUTE) {
    return (
      <div className="page home">
        <header className="home-hero">
          <div>
            <p className="eyebrow">TPBS Security Architecture Studio</p>
            <h1>Identity Security Architecture Hub</h1>
            <p className="lede">
              Build, assess, and publish identity security posture programs with
              structured controls, scoring, and evidence.
            </p>
          </div>
          <div className="hero-card">
            <h2>IAM Assessor</h2>
            <p>
              Run a structured control-by-control assessment and generate a
              snapshot report.
            </p>
            <a className="primary" href={`#${ASSESSOR_ROUTE}`}>
              Launch IAM Assessor
            </a>
          </div>
        </header>

        <section className="home-grid">
          <div className="home-panel">
            <h3>Assessment Framework</h3>
            <p>
              Map identity domains, control objectives, and evidence artifacts
              into a repeatable security architecture practice.
            </p>
          </div>
          <div className="home-panel">
            <h3>Knowledge Base</h3>
            <p>
              Capture findings, risks, and remediation guidance to evolve toward
              a full security architecture reference library.
            </p>
            <a className="ghost-link" href={`#${KNOWLEDGE_ROUTE}`}>
              View knowledge base →
            </a>
          </div>
          <div className="home-panel">
            <h3>Program Metrics</h3>
            <p>
              Track assessed controls, weightings, and report-ready summaries to
              align leadership and delivery teams.
            </p>
          </div>
        </section>
      </div>
    );
  }

  if (loading) {
    return <div className="page">Loading checklist…</div>;
  }

  if (error) {
    return (
      <div className="page">
        <div className="error">{error}</div>
      </div>
    );
  }

  if (!assessment) {
    return <div className="page">No assessment found.</div>;
  }

  const total = assessment.items.length;
  const assessed = assessment.items.filter((item) => item.status === "assessed")
    .length;

  return (
    <div className="page">
      <div className="nav">
        <a className="ghost-link" href={`#${HOME_ROUTE}`}>
          ← Back to index
        </a>
      </div>
      <header className="header">
        <div>
          <h1>{assessment.name}</h1>
          <p>
            Registry hash: <span>{assessment.registry_hash}</span>
          </p>
        </div>
        <div className="summary">
          <div>
            <strong>{assessed}</strong>
            <span>Assessed</span>
          </div>
          <div>
            <strong>{total - assessed}</strong>
            <span>Not assessed</span>
          </div>
          <button className="primary" onClick={handleReport}>
            Generate Report
          </button>
        </div>
      </header>

      {report && (
        <section className="report">
          <h2>Report Snapshot</h2>
          <div className="report-grid">
            <div>
              <span>Overall score</span>
              <strong>{report.summary.overall_score ?? "N/A"}</strong>
            </div>
            <div>
              <span>Controls assessed</span>
              <strong>{report.summary.controls_assessed}</strong>
            </div>
            <div>
              <span>Controls not assessed</span>
              <strong>{report.summary.controls_not_assessed}</strong>
            </div>
          </div>
          <div className="risks">
            <h3>Top Risks</h3>
            {report.top_risks.length === 0 ? (
              <p>No assessed risks yet.</p>
            ) : (
              report.top_risks.map((risk) => (
                <div key={risk.control_id} className="risk">
                  <div>
                    <strong>{risk.control_id}</strong> · {risk.title}
                  </div>
                  <div>
                    Score {risk.score} · Weight {risk.weight}
                  </div>
                </div>
              ))
            )}
          </div>
        </section>
      )}

      {Object.entries(grouped).map(([domain, items]) => (
        <section key={domain} className="domain">
          <h2>{domain}</h2>
          {items.map((item) => (
            <div key={item.control_id} className="card">
              <div className="card-header">
                <div>
                  <h3>
                    {item.control_id} · {item.control.title}
                  </h3>
                  <p>{item.control.objective}</p>
                </div>
                <div className="meta">Weight {item.weight}</div>
              </div>
              <div className="controls">
                <label>
                  Status
                  <select
                    value={item.status}
                    onChange={(e) =>
                      updateLocal(item.control_id, "status", e.target.value)
                    }
                  >
                    <option value="not_assessed">Not assessed</option>
                    <option value="assessed">Assessed</option>
                  </select>
                </label>
                <label>
                  Score
                  <select
                    value={item.score ?? ""}
                    disabled={item.status !== "assessed"}
                    onChange={(e) =>
                      updateLocal(
                        item.control_id,
                        "score",
                        e.target.value === "" ? null : Number(e.target.value)
                      )
                    }
                  >
                    <option value="">Select</option>
                    <option value="0">0</option>
                    <option value="1">1</option>
                    <option value="2">2</option>
                  </select>
                </label>
                <label className="wide">
                  Finding
                  <textarea
                    value={item.finding_text}
                    onChange={(e) =>
                      updateLocal(item.control_id, "finding_text", e.target.value)
                    }
                    placeholder="Document your observation"
                  />
                </label>
                <label className="wide">
                  Evidence refs (comma-separated)
                  <input
                    value={item.evidence_refs.join(", ")}
                    onChange={(e) =>
                      updateLocal(
                        item.control_id,
                        "evidence_refs",
                        e.target.value
                          .split(",")
                          .map((ref) => ref.trim())
                          .filter(Boolean)
                      )
                    }
                    placeholder="ticket-123, screenshot-7"
                  />
                </label>
                <label className="wide">
                  Assessor notes
                  <textarea
                    value={item.assessor_notes}
                    onChange={(e) =>
                      updateLocal(
                        item.control_id,
                        "assessor_notes",
                        e.target.value
                      )
                    }
                    placeholder="Additional context for reviewers"
                  />
                </label>
              </div>
              <div className="actions">
                <button
                  className="ghost"
                  onClick={() => handleSave(item)}
                  disabled={saving === item.control_id}
                >
                  {saving === item.control_id ? "Saving…" : "Save"}
                </button>
              </div>
            </div>
          ))}
        </section>
      ))}
    </div>
  );
}
