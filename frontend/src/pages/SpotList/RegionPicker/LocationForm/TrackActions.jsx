import { Link } from "react-router-dom"

export default function TrackActions({ selection, customName, place, existing, busy, onTrack }) {
  const label = customName.trim()

  return (
    <>
      {existing ? <p>Closest saved launch: {existing.name}</p> : null}
      <div className="actions" style={{ marginTop: 8 }}>
        {existing?.is_tracked ? (
          <Link to={`/spots/${existing.slug}`}>Open {existing.name}</Link>
        ) : null}
        <button
          type="button"
          disabled={Boolean(busy) || !label}
          onClick={() => {
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
          {busy === label ? "Tracking…" : "Track this location"}
        </button>
      </div>
    </>
  )
}
