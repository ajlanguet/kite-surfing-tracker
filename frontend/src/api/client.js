async function getJson(path) {
  const response = await fetch(path)
  if (!response.ok) {
    throw new Error(`${response.status} ${path}`)
  }
  return response.json()
}

async function sendJson(path, body) {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  })
  if (!response.ok) {
    const detail = await response.text()
    throw new Error(detail || `${response.status} ${path}`)
  }
  return response.json()
}

export { getJson, sendJson }
