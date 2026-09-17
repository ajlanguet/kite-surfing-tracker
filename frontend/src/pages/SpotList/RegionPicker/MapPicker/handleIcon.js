import L from "leaflet"

export function handleIcon(kind) {
  const size = kind === "mid" ? 16 : 18
  return L.divIcon({
    className: `leaflet-div-icon box-handle ${kind}`,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
    html: '<span class="handle-square"></span>',
  })
}
