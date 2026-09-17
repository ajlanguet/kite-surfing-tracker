import { cardinal, formatHour, knots } from "../../utils/wind"

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
              <tr key={row.id}>
                <td>{row.local_date}</td>
                <td>{row.rideable_hours}</td>
                <td>{row.fill_in_hour == null ? "—" : formatHour(row.fill_in_hour)}</td>
                <td>{knots(row.mean_wind_kt)}</td>
                <td>{cardinal(row.dominant_direction_deg)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  )
}
