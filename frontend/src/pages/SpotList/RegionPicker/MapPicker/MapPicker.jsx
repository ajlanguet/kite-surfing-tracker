import { useEffect, useRef } from "react"
import L from "leaflet"
import "leaflet/dist/leaflet.css"
import { bindDraw } from "./bindDraw.js"
import { createLeafletMap } from "./createLeafletMap.js"
import { clearSelectionLayers, renderPin, renderPolygonEditor } from "./PolygonEditor.js"
import { renderSpotMarkers } from "./SpotMarkers.js"

function setMapInteraction(map, { mode, hasPolygon }) {
  const drawing = mode === "draw" && !hasPolygon
  if (drawing) {
    map.dragging.disable()
    map.getContainer().style.cursor = "crosshair"
    map.getContainer().classList.add("is-drawing")
    return
  }
  map.dragging.enable()
  map.getContainer().style.cursor = ""
  map.getContainer().classList.remove("is-drawing")
}

export default function MapPicker({ spots, mode, selection, focusTarget, onSelect, onSpotClick }) {
  const rootRef = useRef(null)
  const mapRef = useRef(null)
  const layersRef = useRef({ spots: null, pin: null, shape: null, handles: null })
  const modeRef = useRef(mode)
  const selectionRef = useRef(selection)
  const polygonRef = useRef(selection?.polygon || null)
  const skipFitRef = useRef(false)
  const userMovedRef = useRef(false)
  const fittedSpotsRef = useRef(false)
  const drawRef = useRef({ start: null, box: null })
  const callbacksRef = useRef({ onSelect, onSpotClick })

  modeRef.current = mode
  selectionRef.current = selection
  callbacksRef.current = { onSelect, onSpotClick }

  useEffect(() => {
    const el = rootRef.current
    if (!el) return

    const { map, cleanup } = createLeafletMap(el)
    layersRef.current.spots = L.layerGroup().addTo(map)
    layersRef.current.handles = L.layerGroup().addTo(map)
    mapRef.current = map
    bindDraw(map, { modeRef, selectionRef, skipFitRef, drawRef, callbacksRef })
    const markMoved = () => {
      userMovedRef.current = true
    }
    map.on("zoomstart", markMoved)
    map.on("dragstart", markMoved)

    return () => {
      map.off("zoomstart", markMoved)
      map.off("dragstart", markMoved)
      cleanup()
      mapRef.current = null
    }
  }, [])

  useEffect(() => {
    const map = mapRef.current
    const group = layersRef.current.spots
    if (!map || !group) return
    const fitToSpots = !selection && !userMovedRef.current && !fittedSpotsRef.current
    renderSpotMarkers(map, group, spots, callbacksRef.current.onSpotClick, { fitToSpots })
    if (fitToSpots && spots.length) {
      fittedSpotsRef.current = true
    }
  }, [spots, selection])

  useEffect(() => {
    const map = mapRef.current
    const handleGroup = layersRef.current.handles
    if (!map || !handleGroup) return

    clearSelectionLayers(map, layersRef)

    if (!selection?.polygon?.length) {
      polygonRef.current = null
      skipFitRef.current = true
      userMovedRef.current = true
      return
    }

    renderPin(map, layersRef, selection)
    renderPolygonEditor({
      map,
      layersRef,
      polygon: selection.polygon.map((point) => ({ lat: point.lat, lng: point.lng })),
      polygonRef,
      skipFitRef,
      callbacksRef,
    })
  }, [selection])

  useEffect(() => {
    const map = mapRef.current
    if (!map) return
    setMapInteraction(map, { mode, hasPolygon: Boolean(selection?.polygon) })
  }, [mode, selection])

  useEffect(() => {
    const map = mapRef.current
    if (!map || !focusTarget) return
    userMovedRef.current = true
    skipFitRef.current = true
    if (focusTarget.bounds) {
      map.flyToBounds(focusTarget.bounds, { padding: [36, 36], maxZoom: 14, duration: 0.7 })
      return
    }
    map.flyTo([focusTarget.latitude, focusTarget.longitude], focusTarget.zoom || 12, { duration: 0.7 })
  }, [focusTarget])

  return (
    <div className="map-wrap">
      <div ref={rootRef} className="map-canvas" />
    </div>
  )
}
