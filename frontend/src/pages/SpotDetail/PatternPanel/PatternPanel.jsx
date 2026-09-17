import { formatHour } from "../../../utils/wind"
import HourBar from "./HourBar.jsx"

export default function PatternPanel({ pattern }) {
  return (
    <section className="panel">
      <h2>Pattern so far</h2>
      {pattern?.sample_hours ? (
        <>
          <p>
            Typical fill-in:{" "}
            <strong>
              {pattern.typical_fill_in_hour == null
                ? "not enough held windows yet"
                : formatHour(Math.round(pattern.typical_fill_in_hour))}
            </strong>{" "}
            across {pattern.sample_hours} stored hours.
          </p>
          <div className="hour-bars">
            {Object.entries(pattern.hourly_rideable_probability).map(([hour, probability]) => (
              <HourBar key={hour} hour={hour} probability={probability} />
            ))}
          </div>
        </>
      ) : (
        <p className="empty">Historical pattern needs stored hours. Use Load 30-day history when you want fill-in stats.</p>
      )}
    </section>
  )
}
