export default function PlaceSuggestion({ placeResult, busy, onTrack, onFocus }) {
  return (
    <div className="result-row">
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
  )
}
