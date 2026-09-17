import L from "leaflet"
import { centroid, midpoint, payloadFromPolygon, toLatLngs } from "../geometry.js"
import { bindMidHandles, bindMoveHandle, bindVertexHandles } from "./bindHandles.js"

export function renderPolygonEditor({ map, layersRef, polygon, polygonRef, skipFitRef, callbacksRef }) {
  const handleGroup = layersRef.current.handles
  polygonRef.current = polygon
  const shape = L.polygon(toLatLngs(polygon), {
    color: "#e26d2d",
    weight: 2,
    fillOpacity: 0.12,
    interactive: false,
  }).addTo(map)
  layersRef.current.shape = shape

  const vertexMarkers = []
  const midMarkers = []
  let moveHandle = null

  function paint(next, skipKey) {
    polygonRef.current = next
    shape.setLatLngs(toLatLngs(next))
    const center = centroid(next)
    layersRef.current.pin.setLatLng([center.lat, center.lng])
    if (moveHandle && skipKey !== "move") {
      moveHandle.setLatLng([center.lat, center.lng])
    }
    if (vertexMarkers.length === next.length) {
      next.forEach((point, index) => {
        if (skipKey !== `vertex-${index}`) {
          vertexMarkers[index].setLatLng([point.lat, point.lng])
        }
      })
    }
    if (midMarkers.length === next.length) {
      next.forEach((point, index) => {
        if (skipKey === `mid-${index}`) return
        const other = next[(index + 1) % next.length]
        midMarkers[index].setLatLng(midpoint(point, other))
      })
    }
  }

  function emit(next, preserveName) {
    skipFitRef.current = true
    callbacksRef.current.onSelect(payloadFromPolygon(next), { preserveName })
  }

  const handleApi = { handleGroup, polygonRef, paint, emit }
  bindVertexHandles(polygon, { ...handleApi, vertexMarkers })
  bindMidHandles(polygon, { ...handleApi, midMarkers })
  moveHandle = bindMoveHandle(polygon, handleApi)

  if (!skipFitRef.current) {
    map.fitBounds(shape.getBounds(), { padding: [36, 36] })
    skipFitRef.current = true
  }
}
