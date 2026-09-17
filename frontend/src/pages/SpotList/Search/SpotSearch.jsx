export default function SpotSearch({ query, error, onQueryChange, onSearch }) {
  return (
    <>
      <form className="search-bar" onSubmit={onSearch}>
        <input
          value={query}
          onChange={(event) => onQueryChange(event.target.value)}
          placeholder="Search a town, then pan or click Draw region"
        />
        <button type="submit">Search</button>
      </form>
      {error ? <p className="error">{error}</p> : null}
    </>
  )
}
