import { cardinal, knots } from "../../../utils/wind"

export default function HourRow({ row }) {
  return (
    <tr className={row.rideable ? "rideable" : ""}>
      <td>{row.valid_at.replace("T", " ").slice(0, 16)}</td>
      <td>{knots(row.wind_speed_kt)}</td>
      <td>
        {cardinal(row.wind_direction_deg)} {Number(row.wind_direction_deg || 0).toFixed(0)}°
      </td>
      <td>{row.tide_phase || "—"}</td>
      <td>{row.wave_height_m == null ? "—" : `${Number(row.wave_height_m).toFixed(1)} m`}</td>
      <td>{row.rideable ? "Go" : ""}</td>
    </tr>
  )
}
