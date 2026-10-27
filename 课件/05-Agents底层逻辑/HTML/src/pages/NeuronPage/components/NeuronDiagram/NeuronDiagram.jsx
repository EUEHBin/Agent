import './NeuronDiagram.css'

const weightColor = (w) => (w >= 0 ? '#4dd6c1' : '#ff8a5c')

/**
 * 可复用的「单个神经元」可视化组件（纯展示，通用形式）。
 * 输入/输出仅以文本呈现，神经元用黑白亮度表达激活强度。
 *
 * @param {{key:string,valueText:string,weight:number}[]} inputs
 * @param {number} y     神经元输出值（显示用）
 * @param {number} norm  亮度 ∈ [0,1]：0=纯黑（未激活），1=纯白（强激活）
 */
export default function NeuronDiagram({ inputs, y, norm }) {
  const W = 1000
  const H = 460
  const NEURON = { cx: 520, cy: H / 2, r: 78 }
  const OUT = { x: 860, y: H / 2 }
  const top = 80
  const gap = inputs.length > 1 ? (H - top * 2) / (inputs.length - 1) : 0

  const lum = Math.round(norm * 255)
  const fill = `rgb(${lum}, ${lum}, ${lum})`

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="neuron-svg" preserveAspectRatio="xMidYMid meet">
      <defs>
        <pattern id="neuronGrid" width="32" height="32" patternUnits="userSpaceOnUse">
          <path d="M32 0H0V32" fill="none" stroke="#182430" strokeWidth="1" />
        </pattern>
        <marker id="neuronArrow" markerWidth="12" markerHeight="12" refX="8" refY="5"
          orient="auto" markerUnits="userSpaceOnUse">
          <path d="M0 0 L10 5 L0 10 z" fill="#5c6b7a" />
        </marker>
      </defs>

      <rect x="0" y="0" width={W} height={H} fill="url(#neuronGrid)" opacity="0.5" />

      {inputs.map((it, i) => {
        const cy = top + gap * i
        const x1 = 200
        const x2 = NEURON.cx - NEURON.r * 0.72
        const midX = (x1 + x2) / 2
        const midY = (cy + NEURON.cy) / 2
        const lw = 1.2 + Math.min(Math.abs(it.weight), 2) * 2.2
        return (
          <g key={it.key}>
            <line x1={x1} y1={cy} x2={x2} y2={NEURON.cy}
              stroke={weightColor(it.weight)} strokeWidth={lw}
              strokeLinecap="round" opacity="0.75" />
            <g transform={`translate(${midX}, ${midY})`}>
              <rect x="-38" y="-15" width="76" height="26" rx="13"
                fill="#0c141c" stroke={weightColor(it.weight)} strokeWidth="1" />
              <text x="0" y="3" className="ns-wlabel" fill={weightColor(it.weight)}>
                w{i + 1}={it.weight.toFixed(2)}
              </text>
            </g>
            <text x="188" y={cy + 6} className="ns-input" textAnchor="end">
              {it.key} = {it.valueText}
            </text>
          </g>
        )
      })}

      <line x1={NEURON.cx + NEURON.r + 6} y1={NEURON.cy} x2={OUT.x - 20} y2={OUT.y}
        stroke="#5c6b7a" strokeWidth="3" markerEnd="url(#neuronArrow)" />

      <circle cx={NEURON.cx} cy={NEURON.cy} r={NEURON.r}
        fill={fill} stroke="#5c6b7a" strokeWidth="2" />

      <text x={OUT.x + 4} y={OUT.y + 6} className="ns-output" textAnchor="start">
        y = {y.toFixed(2)}
      </text>
    </svg>
  )
}
