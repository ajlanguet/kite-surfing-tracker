import L from "leaflet"

const TILE_URL = import.meta.env.DEV
  ? "/map-tiles/{z}/{y}/{x}"
  : "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}"

export function createLeafletMap(el) {
  if (el._leaflet_id) {
    el._leaflet_id = null
  }

  const map = L.map(el, {
    center: [25, -40],
    zoom: 3,
    worldCopyJump: true,
    boxZoom: false,
    doubleClickZoom: false,
    scrollWheelZoom: true,
    dragging: true,
    maxZoom: 18,
    minZoom: 2,
  })
  L.tileLayer(TILE_URL, {
    attribution: "Tiles &copy; Esri",
    maxZoom: 18,
  }).addTo(map)

  const resize = () => map.invalidateSize()
  requestAnimationFrame(resize)
  const later = window.setTimeout(resize, 250)
  window.addEventListener("resize", resize)
  const observer = new ResizeObserver(resize)
  observer.observe(el)
  map.on("zoomend", resize)

  return {
    map,
    cleanup() {
      observer.disconnect()
      window.removeEventListener("resize", resize)
      window.clearTimeout(later)
      map.off("zoomend", resize)
      map.remove()
      if (el._leaflet_id) el._leaflet_id = null
    },
  }
}
