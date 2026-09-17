import HourRow from "./HourRow.jsx"

export default function OutlookPanel({ outlook, upcoming }) {
  return (
    <section className="panel">
      <h2>Outlook</h2>
      {outlook ? (
        <p>
          Next hours rideable: <strong>{outlook.rideable_hours}</strong>
          {outlook.next_rideable_at
            ? ` · next window ${outlook.next_rideable_at.replace("T", " ").slice(0, 16)} UTC`
            : " · no rideable hour in the forecast"}
        </p>
      ) : (
        <p className="empty">No forecast stored yet.</p>
      )}
      {upcoming.length > 0 ? (
        <table>
          <thead>
            <tr>
              <th>UTC</th>
              <th>Wind</th>
              <th>Dir</th>
              <th>Tide</th>
              <th>Waves</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {upcoming.map((row) => (
              <HourRow key={row.valid_at} row={row} />
            ))}
          </tbody>
        </table>
      ) : null}
    </section>
  )
}
