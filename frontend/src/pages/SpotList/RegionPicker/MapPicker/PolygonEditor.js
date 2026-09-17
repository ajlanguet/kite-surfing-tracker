import L from "leaflet"
import { centroid, insertVertex, midpoint, payloadFromPolygon, pointFrom, toLatLngs } from "../geometry.js"

function handleIcon(kind) {
  const size = kind === "mid" ? 16 : 18
  return L.divIcon({
    className: `leaflet-div-icon box-handle ${kind}`,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
    html: '<span class="handle-square"></span>',
  })
}

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

  const center = centroid(polygon)
  moveHandle = L.marker([center.lat, center.lng], {
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

  if (!skipFitRef.current) {
    map.fitBounds(shape.getBounds(), { padding: [36, 36] })
    skipFitRef.current = true
  }
}
