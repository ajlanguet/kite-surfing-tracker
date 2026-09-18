import SpotCard from "./SpotCard.jsx"

export default function Watchlist({ spots }) {
  return (
    <>
      <h2 className="section-title">Watchlist</h2>
      {spots.length === 0 ? (
        <p className="empty">Nothing tracked yet. Pick a point on the map or search a name.</p>
      ) : (
        <section className="spot-grid">
          {spots.map((spot) => (
            <SpotCard key={spot.slug} spot={spot} />
          ))}
        </section>
      )}
    </>
  )
}
