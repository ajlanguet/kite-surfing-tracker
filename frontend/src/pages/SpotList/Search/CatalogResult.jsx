import { Link } from "react-router-dom"

export default function CatalogResult({ spot, busy, onTrack, onFocus }) {
  return (
    <div className="result-row">
      <div>
        <strong>{spot.name}</strong>
        <p>{spot.is_tracked ? "Already tracked" : "In the catalog, not storing weather yet."}</p>
      </div>
      <div className="actions" style={{ marginTop: 0 }}>
        <button type="button" className="danger" onClick={() => onFocus(spot)}>
          Show on map
        </button>
        {spot.is_tracked ? (
          <Link to={`/spots/${spot.slug}`}>Open</Link>
        ) : (
          <button type="button" disabled={Boolean(busy)} onClick={() => onTrack({ slug: spot.slug }, spot.name)}>
            {busy === spot.name ? "Tracking…" : "Track"}
          </button>
        )}
      </div>
    </div>
  )
}
