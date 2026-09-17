import { Link } from "react-router-dom"

export default function SearchResults({ results, busy, onTrack, onFocus }) {
  if (!results) return null

  return (
    <section className="panel">
      <h2>Search results</h2>
      {results.spots.map((spot) => (
        <div className="result-row" key={spot.slug}>
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
      ))}
      {results.suggestions.map((placeResult) => (
        <div className="result-row" key={`${placeResult.latitude}-${placeResult.longitude}`}>
          <div>
            <strong>{placeResult.label}</strong>
            <p>New region. Show it on the map, pan to the water, then click Draw region.</p>
          </div>
          <div className="actions" style={{ marginTop: 0 }}>
            <button type="button" className="danger" onClick={() => onFocus(placeResult)}>
              Show on map
            </button>
            <button
              type="button"
              disabled={Boolean(busy)}
              onClick={() => onTrack(placeResult, placeResult.label)}
            >
              {busy === placeResult.label ? "Tracking…" : "Track this region"}
            </button>
          </div>
        </div>
      ))}
      {results.spots.length === 0 && results.suggestions.length === 0 ? (
        <p className="empty">No matches. Try a town or beach name.</p>
      ) : null}
    </section>
  )
}
