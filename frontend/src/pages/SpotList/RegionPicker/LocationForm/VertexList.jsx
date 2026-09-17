import VertexRow from "./VertexRow.jsx"

export default function VertexList({ polygon, onPolygonChange }) {
  if (!polygon?.length) return null

  return (
    <div className="vertex-list">
      {polygon.map((point, index) => (
        <VertexRow
          key={`${index}-${point.lat}-${point.lng}`}
          point={point}
          index={index}
          polygon={polygon}
          onPolygonChange={onPolygonChange}
        />
      ))}
    </div>
  )
}
