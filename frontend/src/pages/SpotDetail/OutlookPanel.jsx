import { cardinal, knots } from "../../utils/wind"

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
              <tr key={row.valid_at} className={row.rideable ? "rideable" : ""}>
                <td>{row.valid_at.replace("T", " ").slice(0, 16)}</td>
                <td>{knots(row.wind_speed_kt)}</td>
                <td>
                  {cardinal(row.wind_direction_deg)} {Number(row.wind_direction_deg || 0).toFixed(0)}°
                </td>
                <td>{row.tide_phase || "—"}</td>
                <td>{row.wave_height_m == null ? "—" : `${Number(row.wave_height_m).toFixed(1)} m`}</td>
                <td>{row.rideable ? "Go" : ""}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : null}
    </section>
  )
}
