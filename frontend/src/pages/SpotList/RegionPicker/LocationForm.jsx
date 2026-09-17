import { Link } from "react-router-dom"
import { selectionFromPolygon } from "./geometry.js"

export default function LocationForm({
  selection,
  customName,
  place,
  existing,
  busy,
  onNameChange,
  onPolygonChange,
  onTrack,
}) {
  return (
    <div className="pick-form">
      <label className="field">
        <span>Location name</span>
        <input
          value={customName}
          onChange={(event) => onNameChange(event.target.value)}
          placeholder="e.g. Secret Hatteras launch"
        />
      </label>
      <p>
        Center {Number(selection.latitude).toFixed(4)}, {Number(selection.longitude).toFixed(4)}
        {place?.timezone ? ` · ${place.timezone}` : ""}
        {selection.polygon ? ` · ${selection.polygon.length}-point region` : ""}
      </p>
      {selection.polygon ? (
        <div className="vertex-list">
          {selection.polygon.map((point, index) => (
            <div className="vertex-row" key={`${index}-${point.lat}-${point.lng}`}>
              <span>P{index + 1}</span>
              <input
                type="number"
                step="0.0001"
                value={point.lat}
                onChange={(event) => {
                  const value = Number(event.target.value)
                  if (!Number.isFinite(value)) return
                  const polygon = selection.polygon.map((item, itemIndex) =>
                    itemIndex === index ? { ...item, lat: value } : item
                  )
                  onPolygonChange(selectionFromPolygon(polygon))
                }}
                aria-label={`Point ${index + 1} latitude`}
              />
              <input
                type="number"
                step="0.0001"
                value={point.lng}
                onChange={(event) => {
                  const value = Number(event.target.value)
                  if (!Number.isFinite(value)) return
                  const polygon = selection.polygon.map((item, itemIndex) =>
                    itemIndex === index ? { ...item, lng: value } : item
                  )
                  onPolygonChange(selectionFromPolygon(polygon))
                }}
                aria-label={`Point ${index + 1} longitude`}
              />
            </div>
          ))}
        </div>
      ) : null}
      {existing ? <p>Closest saved launch: {existing.name}</p> : null}
      <div className="actions" style={{ marginTop: 8 }}>
        {existing?.is_tracked ? (
          <Link to={`/spots/${existing.slug}`}>Open {existing.name}</Link>
        ) : null}
        <button
          type="button"
          disabled={Boolean(busy) || !customName.trim()}
          onClick={() => {
            const label = customName.trim()
            onTrack(
              {
                name: label,
                latitude: selection.latitude,
                longitude: selection.longitude,
                timezone: place?.timezone || "UTC",
                label,
                ...(selection.bounds || {}),
                region_polygon: selection.polygon || undefined,
              },
              label
            )
          }}
        >
          {busy === customName.trim() ? "Tracking…" : "Track this location"}
        </button>
      </div>
    </div>
  )
}
