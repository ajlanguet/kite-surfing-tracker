import { cardinal, formatHour, knots } from "../../../utils/wind"

export default function DayRow({ row }) {
  return (
    <tr>
      <td>{row.local_date}</td>
      <td>{row.rideable_hours}</td>
      <td>{row.fill_in_hour == null ? "—" : formatHour(row.fill_in_hour)}</td>
      <td>{knots(row.mean_wind_kt)}</td>
      <td>{cardinal(row.dominant_direction_deg)}</td>
    </tr>
  )
}
