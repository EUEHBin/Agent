import { useMemo } from 'react'
import MnistDigit from '../../../../components/MnistDigit/MnistDigit.jsx'
import DeltaArrow from '../../../../components/DeltaArrow/DeltaArrow.jsx'
import './BackpropGraph.css'

const LAYERS = [
  { label: '输入层', count: 8, visibleFrom: 99 },
  { label: '隐藏层 1', count: 16, visibleFrom: 6 },
  { label: '隐藏层 2', count: 16, visibleFrom: 4 },
  { label: '输出层', count: 10, visibleFrom: 0 },
]

const W = 1000
const H = 640
const PAD_TOP = 52
const PAD_BOT = 56

const BASE_RGB = [58, 70, 82]
const HI_RGB = [255, 255, 255]

function mixColor(b) {
  const r = Math.round(BASE_RGB[0] + (HI_RGB[0] - BASE_RGB[0]) * b)
  const g = Math.round(BASE_RGB[1] + (HI_RGB[1] - BASE_RGB[1]) * b)
  const bl = Math.round(BASE_RGB[2] + (HI_RGB[2] - BASE_RGB[2]) * b)
  return `rgb(${r}, ${g}, ${bl})`
}

const LABEL_ACTIVATION = [0, 1, 0, 0, 0, 0, 0, 0, 0, 0]
const LABEL_OFFSET_X = 125

/* 整体布局左移：首层 x 与层间距（原为均分 200） */
const START_X = 190
const GAP_X = 155

function buildLayout(layers, h, padTop, padBot) {
  const positions = []
  const maxCount = Math.max(...layers.map((l) => l.count))
  const usableH = h - padTop - padBot
  const gapY = usableH / (maxCount - 1)

  for (let li = 0; li < layers.length; li++) {
    const count = layers[li].count
    const x = START_X + GAP_X * li
    const layerH = gapY * (count - 1)
    const offsetY = padTop + (usableH - layerH) / 2
    const layerNeurons = []
    for (let ni = 0; ni < count; ni++) {
      const y = offsetY + gapY * ni
      layerNeurons.push({ id: `L${li}-N${ni}`, layer: li, index: ni, x, y })
    }
    positions.push(layerNeurons)
  }
  return positions
}

export default function BackpropGraph({
  activations = [null, null, null, null],
  step = 0,
}) {
  const neurons = useMemo(
    () => buildLayout(LAYERS, H, PAD_TOP, PAD_BOT),
    [],
  )

  const maxCount = Math.max(...LAYERS.map((l) => l.count))
  const usableH = H - PAD_TOP - PAD_BOT
  const maxGapY = maxCount > 1 ? usableH / (maxCount - 1) : 100
  const neuronR = Math.max(12, Math.min(18, maxGapY * 0.36))

  const inputX = neurons[0][0].x
  const digitSize = 108
  const digitX = inputX - neuronR - 46 - digitSize
  const digitY = H / 2 - digitSize / 2 - 10

  const outputLayer = LAYERS.length - 1

  const loss = useMemo(() => {
    const out = activations[outputLayer]
    if (!out) return null
    return LABEL_ACTIVATION.reduce(
      (sum, t, i) => sum + (t - out[i]) ** 2,
      0,
    )
  }, [activations, outputLayer])

  const hidden2Arrows = useMemo(
    () =>
      neurons[2].map(() =>
        Array.from({ length: 3 }, () => {
          const sign = Math.random() < 0.5 ? -1 : 1
          return sign * (0.4 + Math.random() * 0.6)
        }),
      ),
    [neurons],
  )

  const hidden2Merged = useMemo(
    () =>
      neurons[2].map(() => {
        const sign = Math.random() < 0.5 ? -1 : 1
        return sign * (0.4 + Math.random() * 0.6)
      }),
    [neurons],
  )

  const hidden1Arrows = useMemo(
    () =>
      neurons[1].map(() =>
        Array.from({ length: 3 }, () => {
          const sign = Math.random() < 0.5 ? -1 : 1
          return sign * (0.4 + Math.random() * 0.6)
        }),
      ),
    [neurons],
  )

  const hidden1Merged = useMemo(
    () =>
      neurons[1].map(() => {
        const sign = Math.random() < 0.5 ? -1 : 1
        return sign * (0.4 + Math.random() * 0.6)
      }),
    [neurons],
  )

  return (
    <svg
      viewBox={`0 0 ${W} ${H}`}
      className="bpg-svg"
      preserveAspectRatio="xMidYMid meet"
    >
      {/* 网格背景 */}
      <defs>
        <pattern id="bpgGrid" width="40" height="40" patternUnits="userSpaceOnUse">
          <path d="M40 0H0V40" fill="none" className="bpg-grid" />
        </pattern>
      </defs>
      <rect x="0" y="0" width={W} height={H} fill="url(#bpgGrid)" opacity="0.35" />

      {/* 层标签（全部显示） */}
      {LAYERS.map((layer, li) => (
        <text
          key={`label-${li}`}
          x={neurons[li][0].x}
          y={H - 16}
          className="bpg-label"
        >
          {layer.label}
        </text>
      ))}

      {/* 输入样本图片（固定显示：第一行第三列，数字 1） */}
      <foreignObject
        x={digitX}
        y={digitY}
        width={digitSize}
        height={digitSize + 26}
        className="bpg-digit-fo"
      >
        <div xmlns="http://www.w3.org/1999/xhtml" className="bpg-digit-wrap">
          <MnistDigit row={0} col={2} />
          <span className="bpg-digit-caption">输入样本</span>
        </div>
      </foreignObject>

      {/* 隐藏层 2 → 输出层连线（STEP 4 出现） */}
      {step >= 4 &&
        neurons[outputLayer].map((dest) => (
          <g key={`conn-${dest.id}`}>
            {neurons[2].map((src) => (
              <line
                key={`${src.id}-${dest.id}`}
                x1={src.x}
                y1={src.y}
                x2={dest.x}
                y2={dest.y}
                className="bpg-conn"
              />
            ))}
          </g>
        ))}

      {/* 隐藏层 1 → 隐藏层 2 连线（STEP 6 出现） */}
      {step >= 6 &&
        neurons[2].map((dest) => (
          <g key={`conn-h1-${dest.id}`}>
            {neurons[1].map((src) => (
              <line
                key={`${src.id}-${dest.id}`}
                x1={src.x}
                y1={src.y}
                x2={dest.x}
                y2={dest.y}
                className="bpg-conn"
              />
            ))}
          </g>
        ))}

      {/* 神经元（仅可见层） */}
      {neurons.map((layerNeurons, li) => {
        if (step < LAYERS[li].visibleFrom) return null
        const layerActivation = activations[li]
        return (
          <g key={`neurons-${li}`}>
            {layerNeurons.map((n) => {
              const b = layerActivation ? layerActivation[n.index] : null
              const activeStyle =
                b != null
                  ? {
                      fill: mixColor(b),
                      filter: `drop-shadow(0 0 ${6 * b}px rgba(255, 255, 255, ${0.65 * b}))`,
                    }
                  : undefined
              const labelFill = b != null && b > 0.5 ? '#0a0d10' : '#ffffff'
              const showValue = li === outputLayer && b != null
              return (
                <g key={n.id} className="bpg-neuron">
                  <circle cx={n.x} cy={n.y} r={neuronR} style={activeStyle} />
                  <text
                    x={n.x}
                    y={n.y + 3.5}
                    className="bpg-neuron-label"
                    style={{ fill: labelFill }}
                  >
                    {li === outputLayer ? n.index : n.index + 1}
                  </text>
                  {showValue && (
                    <text
                      x={n.x + neuronR + 10}
                      y={n.y + 3.5}
                      className="bpg-value"
                    >
                      {b.toFixed(2)}
                    </text>
                  )}
                </g>
              )
            })}
          </g>
        )
      })}

      {/* 标签层（真实结果，STEP 1 出现） */}
      {step >= 1 && (
        <g className="bpg-target">
          <text
            x={neurons[outputLayer][0].x + LABEL_OFFSET_X}
            y={H - 16}
            className="bpg-label"
          >
            标签
          </text>
          {neurons[outputLayer].map((n) => {
            const b = LABEL_ACTIVATION[n.index]
            const x = n.x + LABEL_OFFSET_X
            return (
              <g key={`target-${n.index}`} className="bpg-neuron">
                <circle
                  cx={x}
                  cy={n.y}
                  r={neuronR}
                  style={{
                    fill: mixColor(b),
                    filter: `drop-shadow(0 0 ${6 * b}px rgba(255, 255, 255, ${0.65 * b}))`,
                  }}
                />
                <text
                  x={x}
                  y={n.y + 3.5}
                  className="bpg-neuron-label"
                  style={{ fill: b > 0.5 ? '#0a0d10' : '#ffffff' }}
                >
                  {n.index}
                </text>
                <text
                  x={x + neuronR + 10}
                  y={n.y + 3.5}
                  className="bpg-value"
                >
                  {b.toFixed(2)}
                </text>
              </g>
            )
          })}
        </g>
      )}

      {/* 损失度（STEP 2 出现，标签右侧大字号） */}
      {step >= 2 && loss != null && (
        <g className="bpg-loss">
          <text
            x={neurons[outputLayer][0].x + LABEL_OFFSET_X + neuronR + 78}
            y={H / 2 - 16}
            className="bpg-loss-caption"
          >
            损失度
          </text>
          <text
            x={neurons[outputLayer][0].x + LABEL_OFFSET_X + neuronR + 78}
            y={H / 2 + 22}
            className="bpg-loss-value"
          >
            {loss.toFixed(4)}
          </text>
        </g>
      )}
      {/* 期望箭头（STEP 3 出现，输出神经元左侧） */}
      {step >= 3 &&
        activations[outputLayer] &&
        neurons[outputLayer].map((n) => (
          <DeltaArrow
            key={`delta-${n.index}`}
            x={n.x - neuronR - 16}
            y={n.y}
            value={LABEL_ACTIVATION[n.index] - activations[outputLayer][n.index]}
          />
        ))}

      {/* 对隐藏层 2 的期望箭头（STEP 4：3 个随机箭头 + 省略号；STEP 5：合并为 1 个） */}
      {step === 4 &&
        neurons[2].map((n, ni) => (
          <g key={`h2-delta-${ni}`}>
            {hidden2Arrows[ni].map((v, ai) => (
              <DeltaArrow
                key={ai}
                x={n.x - neuronR - 14 - ai * 15}
                y={n.y}
                value={v}
                minLength={6}
                maxLength={26}
              />
            ))}
            <text
              x={n.x - neuronR - 14 - 3 * 15}
              y={n.y + 4}
              className="bpg-ellipsis"
            >
              ⋯
            </text>
          </g>
        ))}
      {step >= 5 &&
        neurons[2].map((n, ni) => (
          <DeltaArrow
            key={`h2-merged-${ni}`}
            x={n.x - neuronR - 16}
            y={n.y}
            value={hidden2Merged[ni]}
          />
        ))}

      {/* 对隐藏层 1 的期望箭头（STEP 6：3 个随机箭头 + 省略号；STEP 7：合并为 1 个） */}
      {step === 6 &&
        neurons[1].map((n, ni) => (
          <g key={`h1-delta-${ni}`}>
            {hidden1Arrows[ni].map((v, ai) => (
              <DeltaArrow
                key={ai}
                x={n.x - neuronR - 14 - ai * 15}
                y={n.y}
                value={v}
                minLength={6}
                maxLength={26}
              />
            ))}
            <text
              x={n.x - neuronR - 14 - 3 * 15}
              y={n.y + 4}
              className="bpg-ellipsis"
            >
              ⋯
            </text>
          </g>
        ))}
      {step >= 7 &&
        neurons[1].map((n, ni) => (
          <DeltaArrow
            key={`h1-merged-${ni}`}
            x={n.x - neuronR - 16}
            y={n.y}
            value={hidden1Merged[ni]}
          />
        ))}
    </svg>
  )
}
