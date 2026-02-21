const API_BASE = "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });

  if (!res.ok) {
    let detail = "Request failed";
    try {
      const body = await res.json();
      detail = body.detail || JSON.stringify(body);
    } catch {}
    throw new Error(detail);
  }

  const text = await res.text();
  return text ? JSON.parse(text) : null;
}

export const api = {
  // Items
  getItems: (includeInactive = true) =>
    request(`/items?include_inactive=${includeInactive}`),
  createItem: (payload) =>
    request(`/items`, { method: "POST", body: JSON.stringify(payload) }),
  updateItem: (payload) =>
    request(`/items`, { method: "PUT", body: JSON.stringify(payload) }),

  // Waste
  createWaste: (payload) =>
    request(`/waste`, { method: "POST", body: JSON.stringify(payload) }),
  getWaste: ({ startDate, endDate, itemId, limit = 50, offset = 0 }) => {
    const params = new URLSearchParams();
    if (startDate) params.set("start_date", startDate);
    if (endDate) params.set("end_date", endDate);
    if (itemId) params.set("item_id", String(itemId));
    params.set("limit", String(limit));
    params.set("offset", String(offset));
    return request(`/waste?${params.toString()}`);
  },

  // Dashboard
  getDashboard: ({ view = "week", anchorDate }) => {
    const params = new URLSearchParams();
    params.set("view", view);
    if (anchorDate) params.set("anchor_date", anchorDate);
    return request(`/dashboard?${params.toString()}`);
  },

  // Tomorrow plan
  getTomorrowPlan: ({ targetDate } = {}) => {
    const params = new URLSearchParams();
    if (targetDate) params.set("target_date", targetDate);
    return request(`/tomorrow-plan?${params.toString()}`);
  },
};
