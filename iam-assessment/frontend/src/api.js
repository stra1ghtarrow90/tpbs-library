const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export async function getAssessments() {
  const res = await fetch(`${API_BASE}/assessments`);
  if (!res.ok) throw new Error("Failed to load assessments");
  return res.json();
}

export async function createAssessment(payload) {
  const res = await fetch(`${API_BASE}/assessments`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to create assessment");
  return res.json();
}

export async function getAssessment(id) {
  const res = await fetch(`${API_BASE}/assessments/${id}`);
  if (!res.ok) throw new Error("Failed to load assessment");
  return res.json();
}

export async function updateItem(assessmentId, controlId, payload) {
  const res = await fetch(
    `${API_BASE}/assessments/${assessmentId}/items/${controlId}`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }
  );
  if (!res.ok) throw new Error("Failed to update item");
  return res.json();
}

export async function getReport(assessmentId) {
  const res = await fetch(`${API_BASE}/assessments/${assessmentId}/report`);
  if (!res.ok) throw new Error("Failed to generate report");
  return res.json();
}
