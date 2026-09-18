export function focusMap(map, focusTarget) {
  if (focusTarget.bounds) {
    map.flyToBounds(focusTarget.bounds, { padding: [36, 36], maxZoom: 14, duration: 0.7 })
    return
  }
  map.flyTo([focusTarget.latitude, focusTarget.longitude], focusTarget.zoom || 12, { duration: 0.7 })
}
