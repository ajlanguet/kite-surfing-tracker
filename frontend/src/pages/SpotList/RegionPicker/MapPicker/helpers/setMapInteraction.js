export function setMapInteraction(map, { mode, hasPolygon }) {
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
