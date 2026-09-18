import L from "leaflet"
import { payloadFromPolygon, rectanglePolygon } from "../../helpers/geometry.js"

export function bindDraw(map, { modeRef, selectionRef, skipFitRef, drawRef, callbacksRef }) {
  function finishDraw(latlng) {
    if (!drawRef.current.start) return
    const start = drawRef.current.start
    const bounds = L.latLngBounds(start, latlng || start)
    drawRef.current.start = null
    if (drawRef.current.box) {
      drawRef.current.box.remove()
      drawRef.current.box = null
    }
    unbindDocument()
    const drawing = modeRef.current === "draw" && !selectionRef.current?.polygon
    if (bounds.getNorth() === bounds.getSouth() && bounds.getEast() === bounds.getWest()) {
      if (drawing) map.dragging.disable()
      else map.dragging.enable()
      return
    }
    skipFitRef.current = true
    callbacksRef.current.onSelect(payloadFromPolygon(rectanglePolygon(bounds)))
  }

  function onDocumentMove(event) {
    if (!drawRef.current.start || !drawRef.current.box) return
    const latlng = map.mouseEventToLatLng(event)
    drawRef.current.box.setBounds(L.latLngBounds(drawRef.current.start, latlng))
  }

  function onDocumentUp(event) {
    if (!drawRef.current.start) return
    finishDraw(map.mouseEventToLatLng(event))
  }

  function bindDocument() {
    document.addEventListener("mousemove", onDocumentMove)
    document.addEventListener("mouseup", onDocumentUp)
  }

  function unbindDocument() {
    document.removeEventListener("mousemove", onDocumentMove)
    document.removeEventListener("mouseup", onDocumentUp)
  }

  map.on("mousedown", (event) => {
    if (modeRef.current !== "draw") return
    if (event.originalEvent.button !== 0) return
    if (selectionRef.current?.polygon) return
    if (event.originalEvent.target?.closest?.(".box-handle, .leaflet-marker-icon, .leaflet-control")) return
    map.dragging.disable()
    drawRef.current.start = event.latlng
    if (drawRef.current.box) {
      drawRef.current.box.remove()
    }
    drawRef.current.box = L.rectangle(L.latLngBounds(event.latlng, event.latlng), {
      color: "#e26d2d",
      weight: 2,
      fillOpacity: 0.15,
    }).addTo(map)
    bindDocument()
    L.DomEvent.stop(event)
  })

  map.on("remove", unbindDocument)
}
