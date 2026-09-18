import { getJson } from "./client.js"

export function fetchForecasts(slug) {
  return getJson(`/api/weather/${slug}/forecasts/`)
}

export function fetchObservations(slug) {
  return getJson(`/api/weather/${slug}/observations/`)
}

export function fetchSummaries(slug) {
  return getJson(`/api/weather/${slug}/summaries/`)
}

export function fetchPattern(slug) {
  return getJson(`/api/patterns/${slug}/`)
}

export function fetchOutlook(slug) {
  return getJson(`/api/patterns/${slug}/outlook/`)
}
