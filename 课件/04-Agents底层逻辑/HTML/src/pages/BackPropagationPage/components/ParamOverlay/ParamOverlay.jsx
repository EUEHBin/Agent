import { useMemo } from 'react'
import './ParamOverlay.css'

const MATRICES = [
  { title: '隐藏层 1 参数调整', tag: 'ΔW⁽¹⁾ · Δb⁽¹⁾' },
  { title: '隐藏层 2 参数调整', tag: 'ΔW⁽²⁾ · Δb⁽²⁾' },
  { title: '输出层 参数调整', tag: 'ΔW⁽³⁾ · Δb⁽³⁾' },
]

const ROWS = 3
const COLS = 3

function randCell() {
  const sign = Math.random() < 0.5 ? -1 : 1
  const value = sign * (Math.round((0.05 + Math.random() * 0.9) * 100) / 100)
  return { up: value > 0, value }
}

export default function ParamOverlay() {
  const data = useMemo(
    () =>
      MATRICES.map(() => ({
        weights: Array.from({ length: ROWS }, () =>
          Array.from({ length: COLS }, randCell),
        ),
        bias: Array.from({ length: ROWS }, randCell),
      })),
    [],
  )

  return (
    <div className="param-overlay">
      <div className="param-overlay-inner">
        <div className="param-overlay-caption">
          反向传播完成 · 每个参数按梯度方向调整
        </div>
        <div className="param-matrices">
          {MATRICES.map((m, mi) => (
            <div className="param-card" key={m.title}>
              <div className="param-card-head">
                <span className="param-card-title">{m.title}</span>
                <span className="param-card-tag">{m.tag}</span>
              </div>
              <div className="param-body">
                <div className="param-weights">
                  <span className="param-block-label">权重调整 ΔW</span>
                  <div
                    className="param-grid"
                    style={{ gridTemplateColumns: `repeat(${COLS}, 1fr)` }}
                  >
                    {data[mi].weights.flat().map((c, i) => (
                      <ParamCell key={i} cell={c} />
                    ))}
                  </div>
                  <span className="param-ellipsis">⋱</span>
                </div>
                <div className="param-bias">
                  <span className="param-block-label">偏置调整 Δb</span>
                  <div className="param-grid param-grid-bias">
                    {data[mi].bias.map((c, i) => (
                      <ParamCell key={i} cell={c} />
                    ))}
                  </div>
                  <span className="param-ellipsis">⋮</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function ParamCell({ cell }) {
  return (
    <span className="param-cell">
      <span className={`param-value ${cell.up ? 'up' : 'down'}`}>
        {cell.up ? '+' : ''}
        {cell.value.toFixed(2)}
      </span>
      <span className={`param-arrow ${cell.up ? 'up' : 'down'}`}>
        {cell.up ? '▲' : '▼'}
      </span>
    </span>
  )
}
