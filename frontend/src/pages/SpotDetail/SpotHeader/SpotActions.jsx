export default function SpotActions({ spot, busy, onFavorite, onHistory, onUntrack }) {
  return (
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
  )
}
