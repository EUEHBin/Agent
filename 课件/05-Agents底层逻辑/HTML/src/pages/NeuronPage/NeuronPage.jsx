import { useMemo, useState } from 'react'
import NeuronDiagram from './components/NeuronDiagram/NeuronDiagram.jsx'
import NumberField from './components/NumberField.jsx'
import KnobField from './components/KnobField.jsx'
import { computeNeuron } from '../../lib/neuron.js'
import './NeuronPage.css'

// 初始权重 / 偏置（对应 numpy seed 42：randn*0.5）
const W_INIT = { w1: 0.25, w2: -0.07, w3: 0.32, b: 0.76 }

export default function NeuronPage() {
  const [income, setIncome] = useState(50)   // X1 收入
  const [credit, setCredit] = useState(650)  // X2 信用分
  const [debt, setDebt] = useState(30)       // X3 负债率

  const [w1, setW1] = useState(W_INIT.w1)
  const [w2, setW2] = useState(W_INIT.w2)
  const [w3, setW3] = useState(W_INIT.w3)
  const [b, setB] = useState(W_INIT.b)

  const { y, norm, contribs } = useMemo(() => {
    const values = [
      (income ?? 0) / 100,
      ((credit ?? 0) - 300) / 650,
      (debt ?? 0) / 100,
    ]
    return computeNeuron(values, [w1, w2, w3], b)
  }, [income, credit, debt, w1, w2, w3, b])

  // norm = tanh(y) ∈ [0,1)：y=0（未激活）→ 纯黑，y 越大 → 越白
  const inputs = [
    { key: 'X1', valueText: `${income ?? 0}`, weight: w1 },
    { key: 'X2', valueText: `${credit ?? 0}`, weight: w2 },
    { key: 'X3', valueText: `${debt ?? 0}`, weight: w3 },
  ]

  return (
    <div className="npage">
      <div className="npage-head">
        <div>
          <span className="npage-eyebrow">SINGLE NEURON · 感知机</span>
          <h1>单个神经元 — 贷款审批决策</h1>
        </div>
        <code className="npage-formula">z = Σ wᵢxᵢ + b → y = ReLU(z) → tanh(y)</code>
      </div>

      <div className="npage-body">
        <div className="npage-viz">
          <NeuronDiagram inputs={inputs} y={y} norm={norm} />
        </div>

        <aside className="npage-controls">
          <section className="ctl-block">
            <div className="ctl-title"><span className="dot" />输入特征 X</div>
            <NumberField label="X1 · 收入" suffix=" 万/年" min={0} max={100}
              value={income} onChange={setIncome} contrib={contribs[0]} />
            <NumberField label="X2 · 信用分" suffix="" min={300} max={950}
              value={credit} onChange={setCredit} contrib={contribs[1]} />
            <NumberField label="X3 · 负债率" suffix=" %" min={0} max={100}
              value={debt} onChange={setDebt} contrib={contribs[2]} />
          </section>

          <section className="ctl-block">
            <div className="ctl-title"><span className="dot amber" />权重 &amp; 偏置</div>
            <div className="knobs-grid">
              <KnobField label="w₁" value={w1} onChange={setW1} />
              <KnobField label="w₂" value={w2} onChange={setW2} />
              <KnobField label="w₃" value={w3} onChange={setW3} />
              <KnobField label="b" value={b} onChange={setB} accent="#ffb35c" />
            </div>
          </section>
        </aside>
      </div>
    </div>
  )
}
