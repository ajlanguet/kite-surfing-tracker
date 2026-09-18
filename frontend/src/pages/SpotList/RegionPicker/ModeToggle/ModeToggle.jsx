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
