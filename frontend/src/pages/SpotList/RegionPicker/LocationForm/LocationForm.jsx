import NameField from "./NameField.jsx"
import SelectionSummary from "./SelectionSummary.jsx"
import TrackActions from "./TrackActions.jsx"
import VertexList from "./VertexList.jsx"

export default function LocationForm({
  selection,
  customName,
  place,
  existing,
  busy,
  onNameChange,
  onPolygonChange,
  onTrack,
}) {
  return (
    <div className="pick-form">
      <NameField customName={customName} onNameChange={onNameChange} />
      <SelectionSummary selection={selection} place={place} />
      <VertexList polygon={selection.polygon} onPolygonChange={onPolygonChange} />
      <TrackActions
        selection={selection}
        customName={customName}
        place={place}
        existing={existing}
        busy={busy}
        onTrack={onTrack}
      />
    </div>
  )
}
