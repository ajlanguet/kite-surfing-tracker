import { useEffect, useMemo, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"
import {
  fetchOutlook,
  fetchPattern,
  fetchSpot,
  fetchSummaries,
  setFavorite,
  trackPlace,
  untrackSpot,
} from "../../../api"

export function useSpotDetail() {
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

  return { spot, outlook, summaries, pattern, error, busy, upcoming, onFavorite, onHistory, onUntrack }
}
