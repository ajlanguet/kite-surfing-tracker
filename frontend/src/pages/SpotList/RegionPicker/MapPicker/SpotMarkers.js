import L from "leaflet"
import { polygonFromSpot, toLatLngs } from "../geometry.js"

export function renderSpotMarkers(map, group, spots, onSpotClick, { fitToSpots = false } = {}) {
  group.clearLayers()
  const latLngs = []
  spots.forEach((spot) => {
    const lat = Number(spot.latitude)
    const lng = Number(spot.longitude)
    latLngs.push([lat, lng])
    const marker = L.circleMarker([lat, lng], {
      radius: 8,
      color: "#f4efe4",
      fillColor: spot.is_favorite ? "#e26d2d" : "#9fd3c7",
      fillOpacity: 0.95,
      weight: 2,
    }).addTo(group)
    marker.bindTooltip(spot.name)
    marker.on("click", (event) => {
      L.DomEvent.stop(event)
      onSpotClick(spot.slug)
    })
    const outline = polygonFromSpot(spot)
    if (outline) {
      L.polygon(toLatLngs(outline), {
        color: "#9fd3c7",
        weight: 1,
        fillOpacity: 0.08,
        interactive: false,
      }).addTo(group)
    }
  })
  if (fitToSpots && latLngs.length) {
    map.fitBounds(latLngs, { padding: [32, 32], maxZoom: 8 })
  }
  map.invalidateSize()
}
