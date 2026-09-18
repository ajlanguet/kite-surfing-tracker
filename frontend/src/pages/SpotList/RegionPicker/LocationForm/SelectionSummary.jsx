export default function SelectionSummary({ selection, place }) {
  return (
    <p>
      Center {Number(selection.latitude).toFixed(4)}, {Number(selection.longitude).toFixed(4)}
      {place?.timezone ? ` · ${place.timezone}` : ""}
      {selection.polygon ? ` · ${selection.polygon.length}-point region` : ""}
    </p>
  )
}
