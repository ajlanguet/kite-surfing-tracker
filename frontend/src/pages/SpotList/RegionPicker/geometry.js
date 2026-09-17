export function roundCoord(value) {
  return Math.round(Number(value) * 1e6) / 1e6
}

export function pointFrom(latlng) {
  return { lat: roundCoord(latlng.lat), lng: roundCoord(latlng.lng) }
}

export function midpoint(a, b) {
  return {
    lat: roundCoord((a.lat + b.lat) / 2),
    lng: roundCoord((a.lng + b.lng) / 2),
  }
}

export function toLatLngs(polygon) {
  return polygon.map((point) => [point.lat, point.lng])
}

export function centroid(polygon) {
  const lat = polygon.reduce((sum, point) => sum + point.lat, 0) / polygon.length
  const lng = polygon.reduce((sum, point) => sum + point.lng, 0) / polygon.length
  return { lat: roundCoord(lat), lng: roundCoord(lng) }
}

export function insertVertex(polygon, edgeIndex, point) {
  const next = polygon.map((item) => ({ ...item }))
  next.splice(edgeIndex + 1, 0, {
    lat: roundCoord(point.lat),
    lng: roundCoord(point.lng),
  })
  return next
}

export function bboxFromPolygon(polygon) {
  return {
    region_north: roundCoord(Math.max(...polygon.map((point) => point.lat))),
    region_south: roundCoord(Math.min(...polygon.map((point) => point.lat))),
    region_east: roundCoord(Math.max(...polygon.map((point) => point.lng))),
    region_west: roundCoord(Math.min(...polygon.map((point) => point.lng))),
  }
}

export function payloadFromPolygon(polygon) {
  const points = polygon.map((point) => ({
    lat: roundCoord(point.lat),
    lng: roundCoord(point.lng),
  }))
  const center = centroid(points)
  return {
    latitude: center.lat,
    longitude: center.lng,
    polygon: points,
    bounds: bboxFromPolygon(points),
  }
}

export function polygonFromSpot(spot) {
  if (Array.isArray(spot.region_polygon) && spot.region_polygon.length >= 3) {
    return spot.region_polygon
  }
  if (spot.region_north == null) return null
  return [
    { lat: Number(spot.region_north), lng: Number(spot.region_west) },
    { lat: Number(spot.region_north), lng: Number(spot.region_east) },
    { lat: Number(spot.region_south), lng: Number(spot.region_east) },
    { lat: Number(spot.region_south), lng: Number(spot.region_west) },
  ]
}

export function selectionFromPolygon(polygon) {
  const lats = polygon.map((point) => point.lat)
  const lngs = polygon.map((point) => point.lng)
  return {
    latitude: lats.reduce((sum, lat) => sum + lat, 0) / lats.length,
    longitude: lngs.reduce((sum, lng) => sum + lng, 0) / lngs.length,
    polygon,
    bounds: {
      region_north: Math.max(...lats),
      region_south: Math.min(...lats),
      region_east: Math.max(...lngs),
      region_west: Math.min(...lngs),
    },
  }
}

export function rectanglePolygon(bounds) {
  return [
    { lat: bounds.getNorth(), lng: bounds.getWest() },
    { lat: bounds.getNorth(), lng: bounds.getEast() },
    { lat: bounds.getSouth(), lng: bounds.getEast() },
    { lat: bounds.getSouth(), lng: bounds.getWest() },
  ]
}
