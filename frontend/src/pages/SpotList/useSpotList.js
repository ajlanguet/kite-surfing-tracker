import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { fetchSpots, lookupMapPoint, searchPlaces, trackPlace } from "../../api"
import { mapFocusFromPlace } from "./mapFocus.js"

export function useSpotList() {
  const navigate = useNavigate()
  const [spots, setSpots] = useState([])
  const [query, setQuery] = useState("")
  const [results, setResults] = useState(null)
  const [error, setError] = useState("")
  const [busy, setBusy] = useState("")
  const [selection, setSelection] = useState(null)
  const [mapMode, setMapMode] = useState("explore")
  const [picked, setPicked] = useState(null)
  const [customName, setCustomName] = useState("")
  const [nameTouched, setNameTouched] = useState(false)
  const [focusTarget, setFocusTarget] = useState(null)

  function loadSpots() {
    fetchSpots()
      .then(setSpots)
      .catch(() => setError("Could not reach the Django API. Is it running on port 8000?"))
  }

  useEffect(() => {
    loadSpots()
  }, [])

  function focusPlace(place) {
    const target = mapFocusFromPlace(place)
    if (!target) return
    setFocusTarget({ ...target, key: Date.now() })
  }

  async function onSearch(event) {
    event.preventDefault()
    setError("")
    const payload = await searchPlaces(query)
    setResults(payload)
    const first = payload.spots[0] || payload.suggestions[0]
    if (first) focusPlace(first)
  }

  async function onTrack(payload, label) {
    const ok = window.confirm(
      `Track ${label}? We'll store wind for this launch until you remove it. Other regions won't be polled.`
    )
    if (!ok) return
    setBusy(label)
    setError("")
    try {
      const tracked = await trackPlace(payload)
      navigate(`/spots/${tracked.spot.slug}`)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy("")
    }
  }

  function switchMode(nextMode) {
    if (nextMode === "draw" && selection?.polygon) return
    setMapMode(nextMode)
  }

  function clearDrawing() {
    setSelection(null)
    setPicked(null)
    setNameTouched(false)
    setCustomName("")
    setError("")
    setMapMode("explore")
  }

  async function onMapSelect(next, options = {}) {
    setSelection(next)
    setMapMode("explore")
    setError("")
    if (options.preserveName && picked) {
      setPicked({
        ...picked,
        bounds: next.bounds,
        polygon: next.polygon,
        place: {
          ...picked.place,
          latitude: next.latitude,
          longitude: next.longitude,
        },
      })
      return
    }
    try {
      const found = await lookupMapPoint(next.latitude, next.longitude, next.bounds, next.polygon)
      setPicked({ ...found, bounds: next.bounds, polygon: next.polygon })
      if (!nameTouched) {
        setCustomName(found.place?.name || "")
      }
    } catch (err) {
      setError(err.message)
    }
  }

  return {
    spots,
    query,
    results,
    error,
    busy,
    selection,
    mapMode,
    picked,
    customName,
    focusTarget,
    setQuery,
    focusPlace,
    onSearch,
    onTrack,
    switchMode,
    clearDrawing,
    onMapSelect,
    onSpotClick: (slug) => navigate(`/spots/${slug}`),
    onNameChange: (value) => {
      setNameTouched(true)
      setCustomName(value)
    },
    onPolygonChange: (next) => onMapSelect(next, { preserveName: true }),
  }
}
