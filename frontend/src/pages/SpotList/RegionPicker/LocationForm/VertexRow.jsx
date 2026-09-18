import { selectionFromPolygon } from "../helpers/geometry.js"

export default function VertexRow({ point, index, polygon, onPolygonChange }) {
  function updatePoint(field, raw) {
    const value = Number(raw)
    if (!Number.isFinite(value)) return
    const next = polygon.map((item, itemIndex) =>
      itemIndex === index ? { ...item, [field]: value } : item
    )
    onPolygonChange(selectionFromPolygon(next))
  }

  return (
    <div className="vertex-row">
      <span>P{index + 1}</span>
      <input
        type="number"
        step="0.0001"
        value={point.lat}
        onChange={(event) => updatePoint("lat", event.target.value)}
        aria-label={`Point ${index + 1} latitude`}
      />
      <input
        type="number"
        step="0.0001"
        value={point.lng}
        onChange={(event) => updatePoint("lng", event.target.value)}
        aria-label={`Point ${index + 1} longitude`}
      />
    </div>
  )
}
