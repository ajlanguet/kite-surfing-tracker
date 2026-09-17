import { Link } from "react-router-dom"
import { cardinal } from "../../utils/wind"

export default function Watchlist({ spots }) {
  return (
    <>
      <h2 className="section-title">Watchlist</h2>
      {spots.length === 0 ? (
        <p className="empty">Nothing tracked yet. Pick a point on the map or search a name.</p>
      ) : (
        <section className="spot-grid">
          {spots.map((spot) => (
            <Link className="spot-card" key={spot.slug} to={`/spots/${spot.slug}`}>
              <p className="eyebrow">{spot.is_favorite ? "Favorite" : "Tracked"}</p>
              <h2>{spot.name}</h2>
              <p>
                {spot.min_rideable_kt}–{spot.max_rideable_kt} kt · {cardinal(spot.window_start_deg)} to{" "}
                {cardinal(spot.window_end_deg)}
              </p>
              <p className="notes">{spot.notes}</p>
            </Link>
          ))}
        </section>
      )}
    </>
  )
}
