const CARDINALS = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]

export function cardinal(deg) {
  if (deg === null || deg === undefined || Number.isNaN(Number(deg))) return "—"
  return CARDINALS[Math.round(Number(deg) / 22.5) % 16]
}

export function knots(value) {
  if (value === null || value === undefined) return "—"
  return `${Number(value).toFixed(0)} kt`
}

export function formatHour(hour) {
  const value = Number(hour)
  if (Number.isNaN(value)) return "—"
  const suffix = value >= 12 ? "pm" : "am"
  const twelve = value % 12 === 0 ? 12 : value % 12
  return `${twelve}${suffix}`
}
