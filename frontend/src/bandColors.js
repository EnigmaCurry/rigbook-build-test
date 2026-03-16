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
