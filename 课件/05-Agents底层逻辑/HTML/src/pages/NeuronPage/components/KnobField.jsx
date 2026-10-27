import { Knob } from 'primereact/knob'

export default function KnobField({ label, value, onChange, min = -2, max = 2, accent = '#4dd6c1' }) {
  return (
    <div className="knobfield">
      <Knob
        value={value}
        onChange={(e) => onChange(Math.round(e.value * 100) / 100)}
        min={min} max={max} step={0.05} size={62} strokeWidth={9}
        valueColor={accent} rangeColor="#243441" textColor="#e7eef4"
      />
      <span className="knoblabel">{label}</span>
    </div>
  )
}
