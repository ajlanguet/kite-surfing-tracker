export function mapFocusFromPlace(place) {
  if (!place) return null
  if (
    place.region_north != null &&
    place.region_south != null &&
    place.region_east != null &&
    place.region_west != null
  ) {
    return {
      bounds: [
        [Number(place.region_south), Number(place.region_west)],
        [Number(place.region_north), Number(place.region_east)],
      ],
    }
  }
  if (Array.isArray(place.region_polygon) && place.region_polygon.length >= 2) {
    const lats = place.region_polygon.map((point) => Number(point.lat))
    const lngs = place.region_polygon.map((point) => Number(point.lng))
    return {
      bounds: [
        [Math.min(...lats), Math.min(...lngs)],
        [Math.max(...lats), Math.max(...lngs)],
      ],
    }
  }
  const latitude = Number(place.latitude)
  const longitude = Number(place.longitude)
  if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) return null
  return { latitude, longitude, zoom: 12 }
}
