export function parkAward(count) {
  if (count >= 20) return "🏆";
  if (count >= 15) return "💎";
  if (count >= 10) return "🌟";
  if (count >= 5) return "⭐";
  if (count >= 4) return "🍀";
  if (count >= 3) return "📐";
  if (count >= 2) return "✌️";
  if (count >= 1) return "✅";
  return "";
}

export function parkAwardTitle(count) {
  if (count >= 20) return "20+ QSOs";
  if (count >= 15) return "15+ QSOs";
  if (count >= 10) return "10+ QSOs";
  if (count >= 5) return "5+ QSOs";
  if (count >= 4) return "4 QSOs";
  if (count >= 3) return "3 QSOs";
  if (count >= 2) return "2 QSOs";
  if (count >= 1) return "First contact";
  return "";
}
