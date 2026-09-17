import { useEffect, useMemo, useState } from "react"
import { Link, useNavigate, useParams } from "react-router-dom"
import {
  fetchOutlook,
  fetchPattern,
  fetchSpot,
  fetchSummaries,
  setFavorite,
  trackPlace,
  untrackSpot,
} from "../../api"
import OutlookPanel from "./OutlookPanel.jsx"
import PatternPanel from "./PatternPanel.jsx"
import RecentDaysPanel from "./RecentDaysPanel.jsx"
import SpotHeader, { SpotDetailNav } from "./SpotHeader.jsx"

export default function SpotDetail() {
  const { slug } = useParams()
  const navigate = useNavigate()
  const [spot, setSpot] = useState(null)
  const [outlook, setOutlook] = useState(null)
  const [summaries, setSummaries] = useState([])
  const [pattern, setPattern] = useState(null)
  const [error, setError] = useState("")
  const [busy, setBusy] = useState("")

  function load() {
    Promise.all([fetchSpot(slug), fetchOutlook(slug), fetchSummaries(slug), fetchPattern(slug)])
      .then(([nextSpot, nextOutlook, nextSummaries, nextPattern]) => {
        setSpot(nextSpot)
        setOutlook(nextOutlook)
        setSummaries(nextSummaries)
        setPattern(nextPattern)
      })
      .catch(() => setError("Could not load this spot."))
  }

  useEffect(() => {
    load()
  }, [slug])

  const upcoming = useMemo(() => outlook?.hours?.slice(0, 24) || [], [outlook])

  async function onFavorite() {
    await setFavorite(slug, !spot.is_favorite)
    load()
  }

  async function onHistory() {
    setBusy("history")
    await trackPlace({ slug, history_days: 30 })
    setBusy("")
    load()
  }

  async function onUntrack() {
    const ok = window.confirm(
      `Stop tracking ${spot.name}? Stored forecasts, observations, and summaries for this region will be deleted.`
    )
    if (!ok) return
    setBusy("untrack")
    const result = await untrackSpot(slug)
    navigate("/")
    return result
  }

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
