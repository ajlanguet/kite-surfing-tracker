import { formatHour } from "../../../utils/wind"

export default function HourBar({ hour, probability }) {
  return (
    <div className="hour-bar">
      <span>{formatHour(hour)}</span>
      <b style={{ height: `${Math.max(8, probability * 120)}px` }} title={`${Math.round(probability * 100)}%`} />
      <small>{Math.round(probability * 100)}%</small>
    </div>
  )
}
