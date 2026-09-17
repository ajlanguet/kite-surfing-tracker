import LocationForm from "./LocationForm.jsx"
import MapPicker from "./MapPicker"
import ModeToggle, { modeHint } from "./ModeToggle.jsx"

export default function RegionPicker({
  spots,
  mapMode,
  selection,
  customName,
  place,
  existing,
  busy,
  onSwitchMode,
  onSelect,
  onSpotClick,
  onNameChange,
  onPolygonChange,
  onTrack,
  onClear,
  focusTarget,
}) {
  const hasDrawing = Boolean(selection?.polygon)
  return (
    <section className="panel map-panel">
      <ModeToggle mapMode={mapMode} hasDrawing={hasDrawing} onSwitchMode={onSwitchMode} onClear={onClear} />
      <p className="notes">{modeHint(mapMode, selection)}</p>
      <MapPicker
        spots={spots}
        mode={mapMode}
        selection={selection}
        focusTarget={focusTarget}
        onSelect={onSelect}
        onSpotClick={onSpotClick}
      />
      {hasDrawing ? (
        <LocationForm
          selection={selection}
          customName={customName}
          place={place}
          existing={existing}
          busy={busy}
          onNameChange={onNameChange}
          onPolygonChange={onPolygonChange}
          onTrack={onTrack}
        />
      ) : null}
    </section>
  )
}
