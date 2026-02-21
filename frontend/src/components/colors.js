export const PALETTE = [
  "#2563eb", "#16a34a", "#ea580c", "#7c3aed", "#dc2626",
  "#0891b2", "#ca8a04", "#be185d", "#4b5563", "#0f766e",
];

export function colorForId(id) {
  const idx = Math.abs(Number(id || 0)) % PALETTE.length;
  return PALETTE[idx];
}
