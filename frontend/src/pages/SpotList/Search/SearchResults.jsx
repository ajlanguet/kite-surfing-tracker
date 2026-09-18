import CatalogResult from "./CatalogResult.jsx"
import PlaceSuggestion from "./PlaceSuggestion.jsx"

export default function SearchResults({ results, busy, onTrack, onFocus }) {
  if (!results) return null

  return (
    <section className="panel">
      <h2>Search results</h2>
      {results.spots.map((spot) => (
        <CatalogResult key={spot.slug} spot={spot} busy={busy} onTrack={onTrack} onFocus={onFocus} />
      ))}
      {results.suggestions.map((placeResult) => (
        <PlaceSuggestion
          key={`${placeResult.latitude}-${placeResult.longitude}`}
          placeResult={placeResult}
          busy={busy}
          onTrack={onTrack}
          onFocus={onFocus}
        />
      ))}
      {results.spots.length === 0 && results.suggestions.length === 0 ? (
        <p className="empty">No matches. Try a town or beach name.</p>
      ) : null}
    </section>
  )
}
