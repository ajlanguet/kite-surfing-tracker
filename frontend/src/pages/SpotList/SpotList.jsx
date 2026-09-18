import RegionPicker from "./RegionPicker"
import SpotSearch from "./Search"
import SearchResults from "./Search/SearchResults.jsx"
import SpotListHero from "./SpotListHero.jsx"
import Watchlist from "./Watchlist"
import { useSpotList } from "./helpers/useSpotList.js"

export default function SpotList() {
  const list = useSpotList()

  return (
    <main className="page">
      <SpotListHero />
      <SpotSearch
        query={list.query}
        error={list.error}
        onQueryChange={list.setQuery}
        onSearch={list.onSearch}
      />
      <RegionPicker
        spots={list.spots}
        mapMode={list.mapMode}
        selection={list.selection}
        customName={list.customName}
        place={list.picked?.place}
        existing={list.picked?.existing_spot}
        busy={list.busy}
        focusTarget={list.focusTarget}
        onSwitchMode={list.switchMode}
        onSelect={list.onMapSelect}
        onSpotClick={list.onSpotClick}
        onNameChange={list.onNameChange}
        onPolygonChange={list.onPolygonChange}
        onTrack={list.onTrack}
        onClear={list.clearDrawing}
      />
      <SearchResults results={list.results} busy={list.busy} onTrack={list.onTrack} onFocus={list.focusPlace} />
      <Watchlist spots={list.spots} />
    </main>
  )
}
