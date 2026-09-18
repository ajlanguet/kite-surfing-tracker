import DayRow from "./DayRow.jsx"

export default function RecentDaysPanel({ summaries }) {
  return (
    <section className="panel">
      <h2>Recent days</h2>
      {summaries.length === 0 ? (
        <p className="empty">No daily summaries yet.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Rideable hrs</th>
              <th>Fill-in</th>
              <th>Mean</th>
              <th>Dir</th>
            </tr>
          </thead>
          <tbody>
            {summaries.slice(0, 14).map((row) => (
              <DayRow key={row.id} row={row} />
            ))}
          </tbody>
        </table>
      )}
    </section>
  )
}
