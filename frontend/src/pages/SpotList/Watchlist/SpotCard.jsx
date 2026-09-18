import { Link } from "react-router-dom"
import { cardinal } from "../../../utils/wind"

export default function SpotCard({ spot }) {
  return (
    <Link className="spot-card" to={`/spots/${spot.slug}`}>
      <p className="eyebrow">{spot.is_favorite ? "Favorite" : "Tracked"}</p>
      <h2>{spot.name}</h2>
      <p>
        {spot.min_rideable_kt}–{spot.max_rideable_kt} kt · {cardinal(spot.window_start_deg)} to{" "}
        {cardinal(spot.window_end_deg)}
      </p>
      <p className="notes">{spot.notes}</p>
    </Link>
  )
}
