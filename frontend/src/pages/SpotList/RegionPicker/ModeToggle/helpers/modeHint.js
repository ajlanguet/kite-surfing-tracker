export function modeHint(mapMode, selection) {
  if (selection?.polygon) {
    return "Drag a corner or side square to reshape. Drag the center circle to move the region. Drag the map to pan, scroll to zoom."
  }
  if (mapMode === "draw") {
    return "Click and drag a box over the water you ride. Choose Move around if you need to pan first."
  }
  return "Drag the map to pan, scroll to zoom, or search a town. Click Draw region when you are ready to outline the water."
}
