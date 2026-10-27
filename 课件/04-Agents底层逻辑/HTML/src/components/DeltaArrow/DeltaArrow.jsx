import './DeltaArrow.css'

export default function DeltaArrow({
  x = 0,
  y = 0,
  value = 0,
  minLength = 8,
  maxLength = 34,
}) {
  if (value === 0) return null
  const up = value > 0
  const mag = Math.min(Math.abs(value), 1)
  const len = minLength + (maxLength - minLength) * mag
  const strokeWidth = 1.5 + 2.5 * mag
  const headW = 3.5 + 4.5 * mag
  const headH = 4.5 + 5 * mag

  const tail = up ? y + len / 2 : y - len / 2
  const tip = up ? y - len / 2 : y + len / 2
  const headBase = up ? tip + headH : tip - headH

  return (
    <g className={`delta-arrow ${up ? 'up' : 'down'}`}>
      <line
        x1={x}
        y1={tail}
        x2={x}
        y2={headBase}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
      />
      <polygon
        points={`${x - headW},${headBase} ${x + headW},${headBase} ${x},${tip}`}
      />
    </g>
  )
}
