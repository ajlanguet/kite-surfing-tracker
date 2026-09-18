import { cardinal } from "../../../utils/wind"
import SpotActions from "./SpotActions.jsx"

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
      <SpotActions
        spot={spot}
        busy={busy}
        onFavorite={onFavorite}
        onHistory={onHistory}
        onUntrack={onUntrack}
      />
    </header>
  )
}
