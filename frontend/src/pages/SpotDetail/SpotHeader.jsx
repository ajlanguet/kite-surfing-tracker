import { Link } from "react-router-dom"
import { cardinal } from "../../utils/wind"

export default function SpotHeader({ spot, busy, onFavorite, onHistory, onUntrack }) {
  return (
    <header className="hero">
      <p className="eyebrow">{spot.timezone}</p>
      <h1>{spot.name}</h1>
      <p className="lede">
        Rideable {spot.min_rideable_kt}–{spot.max_rideable_kt} kt from {cardinal(spot.window_start_deg)} to{" "}
        {cardinal(spot.window_end_deg)}
        {spot.tide_preference && spot.tide_preference !== "any" ? ` · tide: ${spot.tide_preference}` : ""}.
      </p>
      <div className="actions">
        <button type="button" onClick={onFavorite}>
          {spot.is_favorite ? "Unfavorite" : "Favorite"}
        </button>
        <button type="button" disabled={busy === "history"} onClick={onHistory}>
          {busy === "history" ? "Loading history…" : "Load 30-day history"}
        </button>
        <button type="button" className="danger" disabled={busy === "untrack"} onClick={onUntrack}>
          Stop tracking
        </button>
      </div>
    </header>
  )
}

export function SpotDetailNav() {
  return (
    <p>
      <Link to="/">Watchlist</Link>
    </p>
  )
}
