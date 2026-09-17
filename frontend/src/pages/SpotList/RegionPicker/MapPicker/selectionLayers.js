import L from "leaflet"

export function clearSelectionLayers(map, layersRef) {
  if (layersRef.current.pin) {
    layersRef.current.pin.remove()
    layersRef.current.pin = null
  }
  if (layersRef.current.shape) {
    layersRef.current.shape.remove()
    layersRef.current.shape = null
  }
  layersRef.current.handles.clearLayers()
}

export function renderPin(map, layersRef, selection) {
  layersRef.current.pin = L.circleMarker([selection.latitude, selection.longitude], {
    radius: 9,
    color: "#10232b",
    fillColor: "#e26d2d",
    fillOpacity: 1,
    weight: 2,
    interactive: false,
  }).addTo(map)
}
