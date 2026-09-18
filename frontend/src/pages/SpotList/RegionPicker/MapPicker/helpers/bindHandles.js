import L from "leaflet"
import { centroid, insertVertex, midpoint, pointFrom } from "../../helpers/geometry.js"
import { handleIcon } from "./handleIcon.js"

export function bindVertexHandles(polygon, { handleGroup, polygonRef, paint, emit, vertexMarkers }) {
  polygon.forEach((point, index) => {
    const marker = L.marker([point.lat, point.lng], {
      draggable: true,
      autoPan: true,
      autoPanPadding: [48, 48],
      icon: handleIcon("vertex"),
      zIndexOffset: 1200,
      keyboard: false,
      title: "Drag this corner to reshape.",
    }).addTo(handleGroup)
    marker.on("drag", (event) => {
      const next = polygonRef.current.map((item) => ({ ...item }))
      next[index] = pointFrom(event.target.getLatLng())
      paint(next, `vertex-${index}`)
    })
    marker.on("dragend", () => emit(polygonRef.current, true))
    marker.on("dblclick", (event) => {
      L.DomEvent.stop(event)
      if (polygonRef.current.length <= 3) return
      emit(
        polygonRef.current.filter((_, itemIndex) => itemIndex !== index),
        true
      )
    })
    vertexMarkers.push(marker)
  })
}

export function bindMidHandles(polygon, { handleGroup, polygonRef, paint, emit, midMarkers }) {
  polygon.forEach((point, index) => {
    const other = polygon[(index + 1) % polygon.length]
    const mid = midpoint(point, other)
    const marker = L.marker([mid.lat, mid.lng], {
      draggable: true,
      autoPan: true,
      autoPanPadding: [48, 48],
      icon: handleIcon("mid"),
      zIndexOffset: 1100,
      keyboard: false,
      title: "Drag this side to add a corner and reshape.",
    }).addTo(handleGroup)
    const edgeOrigin = { polygon: null }
    marker.on("dragstart", () => {
      edgeOrigin.polygon = polygonRef.current.map((item) => ({ ...item }))
    })
    marker.on("drag", (event) => {
      if (!edgeOrigin.polygon) return
      paint(insertVertex(edgeOrigin.polygon, index, pointFrom(event.target.getLatLng())), `mid-${index}`)
    })
    marker.on("dragend", () => {
      if (!edgeOrigin.polygon || polygonRef.current.length === edgeOrigin.polygon.length) return
      emit(polygonRef.current, true)
    })
    midMarkers.push(marker)
  })
}

export function bindMoveHandle(polygon, { handleGroup, polygonRef, paint, emit }) {
  const center = centroid(polygon)
  const moveHandle = L.marker([center.lat, center.lng], {
    draggable: true,
    autoPan: true,
    autoPanPadding: [48, 48],
    icon: handleIcon("move"),
    zIndexOffset: 1300,
    keyboard: false,
    title: "Drag to move the whole shape.",
  }).addTo(handleGroup)
  const moveOrigin = { polygon: null, latlng: null }
  moveHandle.on("dragstart", (event) => {
    moveOrigin.polygon = polygonRef.current.map((item) => ({ ...item }))
    moveOrigin.latlng = event.target.getLatLng()
  })
  moveHandle.on("drag", (event) => {
    if (!moveOrigin.polygon) return
    const now = event.target.getLatLng()
    const dlat = now.lat - moveOrigin.latlng.lat
    const dlng = now.lng - moveOrigin.latlng.lng
    paint(
      moveOrigin.polygon.map((item) => ({ lat: item.lat + dlat, lng: item.lng + dlng })),
      "move"
    )
  })
  moveHandle.on("dragend", () => emit(polygonRef.current, true))
  return moveHandle
}
