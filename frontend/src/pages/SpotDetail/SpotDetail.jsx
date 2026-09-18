import { Link } from "react-router-dom"
import OutlookPanel from "./OutlookPanel"
import PatternPanel from "./PatternPanel"
import RecentDaysPanel from "./RecentDaysPanel"
import SpotHeader, { SpotDetailNav } from "./SpotHeader"
import { useSpotDetail } from "./helpers/useSpotDetail.js"

export default function SpotDetail() {
  const { spot, outlook, summaries, pattern, error, busy, upcoming, onFavorite, onHistory, onUntrack } =
    useSpotDetail()

  if (error) {
    return (
      <main className="page">
        <p className="error">{error}</p>
        <Link to="/">Back to watchlist</Link>
      </main>
    )
  }

  if (!spot) {
    return (
      <main className="page">
        <p>Loading…</p>
      </main>
    )
  }

  return (
    <main className="page">
      <SpotDetailNav />
      <SpotHeader
        spot={spot}
        busy={busy}
        onFavorite={onFavorite}
        onHistory={onHistory}
        onUntrack={onUntrack}
      />
      <OutlookPanel outlook={outlook} upcoming={upcoming} />
      <PatternPanel pattern={pattern} />
      <RecentDaysPanel summaries={summaries} />
    </main>
  )
}
