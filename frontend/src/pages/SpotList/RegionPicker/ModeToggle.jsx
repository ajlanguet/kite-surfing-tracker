export default function ModeToggle({ mapMode, hasDrawing, onSwitchMode, onClear }) {
  const drawArmed = mapMode === "draw" && !hasDrawing
  return (
    <div className="actions" style={{ marginTop: 0, marginBottom: 12 }}>
      <button type="button" className={drawArmed ? "danger" : ""} onClick={() => onSwitchMode("explore")}>
        Move around
      </button>
      <button type="button" className={drawArmed ? "" : "danger"} onClick={() => onSwitchMode("draw")}>
        Draw region
      </button>
      {hasDrawing ? (
        <button type="button" className="danger" onClick={onClear}>
          Clear drawing
        </button>
      ) : null}
    </div>
  )
}

export function modeHint(mapMode, selection) {
  if (selection?.polygon) {
    return "Drag a corner or side square to reshape. Drag the center circle to move the region. Drag the map to pan, scroll to zoom."
  }
  if (mapMode === "draw") {
    return "Click and drag a box over the water you ride. Choose Move around if you need to pan first."
  }
  return "Drag the map to pan, scroll to zoom, or search a town. Click Draw region when you are ready to outline the water."
}
