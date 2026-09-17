export default function NameField({ customName, onNameChange }) {
  return (
    <label className="field">
      <span>Location name</span>
      <input
        value={customName}
        onChange={(event) => onNameChange(event.target.value)}
        placeholder="e.g. Secret Hatteras launch"
      />
    </label>
  )
}
