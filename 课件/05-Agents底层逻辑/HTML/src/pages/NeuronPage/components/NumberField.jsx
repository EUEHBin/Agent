import { InputNumber } from 'primereact/inputnumber'

export default function NumberField({ label, suffix, min, max, value, onChange, contrib }) {
  return (
    <div className="numfield">
      <div className="numfield-row">
        <label>{label}</label>
        <span className="contrib">w·x = {contrib >= 0 ? '+' : ''}{contrib.toFixed(3)}</span>
      </div>
      <InputNumber
        value={value}
        onValueChange={(e) => onChange(e.value ?? 0)}
        min={min} max={max} suffix={suffix}
        showButtons buttonLayout="horizontal"
        incrementButtonIcon="pi pi-plus" decrementButtonIcon="pi pi-minus"
        inputClassName="num-input"
      />
    </div>
  )
}
