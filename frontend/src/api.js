async function getJson(path) {
  const response = await fetch(path)
  if (!response.ok) {
    throw new Error(`${response.status} ${path}`)
  }
  return response.json()
}

async function sendJson(path, body) {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  })
  if (!response.ok) {
    const detail = await response.text()
    throw new Error(detail || `${response.status} ${path}`)
  }
  return response.json()
}

export function fetchSpots() {
  return getJson("/api/spots/")
}

export function fetchSpot(slug) {
  return getJson(`/api/spots/${slug}/`)
}

export function searchPlaces(query) {
  return getJson(`/api/spots/search/?q=${encodeURIComponent(query)}`)
}

export function lookupMapPoint(latitude, longitude, bounds, polygon) {
  const params = new URLSearchParams({
    latitude: String(latitude),
    longitude: String(longitude),
  })
  if (bounds) {
    ;["region_north", "region_south", "region_east", "region_west"].forEach((key) => {
      if (bounds[key] != null) params.set(key, String(bounds[key]))
    })
  }
  if (polygon?.length) {
    params.set("region_polygon", JSON.stringify(polygon))
  }
  return getJson(`/api/spots/from-point/?${params.toString()}`)
}

export function trackPlace(payload) {
  return sendJson("/api/spots/track/", payload)
}

export function untrackSpot(slug) {
  return sendJson(`/api/spots/${slug}/untrack/`, {})
}

export function setFavorite(slug, isFavorite) {
  return sendJson(`/api/spots/${slug}/favorite/`, { is_favorite: isFavorite })
}

export function fetchForecasts(slug) {
  return getJson(`/api/weather/${slug}/forecasts/`)
}

export function fetchObservations(slug) {
  return getJson(`/api/weather/${slug}/observations/`)
}

export function fetchSummaries(slug) {
  return getJson(`/api/weather/${slug}/summaries/`)
}

export function fetchPattern(slug) {
  return getJson(`/api/patterns/${slug}/`)
}

export function fetchOutlook(slug) {
  return getJson(`/api/patterns/${slug}/outlook/`)
}
