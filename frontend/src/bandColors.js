// Consistent band colors — gradient from low freq (warm) to high freq (cool)
const BAND_COLORS = {
  "160m": "#e64553",
  "80m":  "#e67e22",
  "60m":  "#e6a700",
  "40m":  "#d4b800",
  "30m":  "#a6d100",
  "20m":  "#40b93c",
  "17m":  "#2db88a",
  "15m":  "#2aa5b8",
  "12m":  "#3a8fd4",
  "10m":  "#5b6abf",
  "6m":   "#8b5ec4",
  "2m":   "#c75ec4",
};

export function bandColor(bandName) {
  return BAND_COLORS[bandName] || "var(--accent)";
}

// Return black or white text for best contrast against the band color
export function bandTextColor(bandName) {
  const hex = BAND_COLORS[bandName];
  if (!hex) return "#fff";
  const r = parseInt(hex.slice(1, 3), 16) / 255;
  const g = parseInt(hex.slice(3, 5), 16) / 255;
  const b = parseInt(hex.slice(5, 7), 16) / 255;
  // Relative luminance (sRGB)
  const L = 0.2126 * r + 0.7152 * g + 0.0722 * b;
  return L > 0.45 ? "#000" : "#fff";
}
