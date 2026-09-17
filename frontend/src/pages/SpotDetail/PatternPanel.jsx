import { formatHour } from "../../utils/wind"

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
              <div className="hour-bar" key={hour}>
                <span>{formatHour(hour)}</span>
                <b style={{ height: `${Math.max(8, probability * 120)}px` }} title={`${Math.round(probability * 100)}%`} />
                <small>{Math.round(probability * 100)}%</small>
              </div>
            ))}
          </div>
        </>
      ) : (
        <p className="empty">Historical pattern needs stored hours. Use Load 30-day history when you want fill-in stats.</p>
      )}
    </section>
  )
}
