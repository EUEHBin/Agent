import { useState, useMemo, useCallback } from 'react'
import MnistDigit from '../../../../components/MnistDigit/MnistDigit.jsx'
import './NetworkGraph.css'

const LAYERS = [
  { label: '输入层', count: 8 },
  { label: '隐藏层 1', count: 16 },
  { label: '隐藏层 2', count: 16 },
  { label: '输出层', count: 10 },
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

function buildLayout(layers, w, h, padTop, padBot) {
  const positions = []
  const maxCount = Math.max(...layers.map((l) => l.count))
  const usableH = h - padTop - padBot
  const gapX = w / (layers.length + 1)
  const gapY = usableH / (maxCount - 1)

  for (let li = 0; li < layers.length; li++) {
    const count = layers[li].count
    const x = gapX * (li + 1)
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

export default function NetworkGraph({
  activations = [null, null, null, null],
  showDigit = false,
  digitKey = 0,
}) {
  const [hovered, setHovered] = useState(null)

  const neurons = useMemo(
    () => buildLayout(LAYERS, W, H, PAD_TOP, PAD_BOT),
    [],
  )

  const handleEnter = useCallback((layer, index) => {
    setHovered({ layer, index })
  }, [])

  const handleLeave = useCallback(() => {
    setHovered(null)
  }, [])

  const maxCount = Math.max(...LAYERS.map((l) => l.count))
  const gapX = W / (LAYERS.length + 1)
  const usableH = H - PAD_TOP - PAD_BOT
  const maxGapY = maxCount > 1 ? usableH / (maxCount - 1) : 100
  const neuronR = Math.max(12, Math.min(18, maxGapY * 0.36))

  const inputX = gapX
  const digitSize = 108
  const digitX = inputX - neuronR - 46 - digitSize
  const digitY = H / 2 - digitSize / 2 - 10

  const outputLayer = LAYERS.length - 1
  const outputActivation = activations[outputLayer]
  const softmax = useMemo(() => {
    if (!outputActivation) return null
    const max = Math.max(...outputActivation)
    const exps = outputActivation.map((v) => Math.exp(v - max))
    const sum = exps.reduce((a, c) => a + c, 0)
    return exps.map((e) => e / sum)
  }, [outputActivation])
  const topIndex = useMemo(
    () => (softmax ? softmax.indexOf(Math.max(...softmax)) : -1),
    [softmax],
  )

  return (
    <svg
      viewBox={`0 0 ${W} ${H}`}
      className="nng-svg"
      preserveAspectRatio="xMidYMid meet"
    >
      {/* 网格背景 */}
      <defs>
        <pattern id="nngGrid" width="40" height="40" patternUnits="userSpaceOnUse">
          <path d="M40 0H0V40" fill="none" className="nng-grid" />
        </pattern>
      </defs>
      <rect x="0" y="0" width={W} height={H} fill="url(#nngGrid)" opacity="0.35" />

      {/* 层标签 */}
      {LAYERS.map((layer, li) => (
        <text
          key={`label-${li}`}
          x={gapX * (li + 1)}
          y={H - 16}
          className="nng-label"
        >
          {layer.label}
        </text>
      ))}

      {/* 连线：从前一层到当前层的每个神经元 */}
      {neurons.slice(1).map((layerNeurons, li) => {
        const destLayer = li + 1
        const srcLayer = li
        const srcNeurons = neurons[li]
        const srcActivation =
          activations[destLayer] != null ? activations[srcLayer] : null
        return (
          <g key={`conns-${destLayer}`}>
            {layerNeurons.map((dest) => {
              const isConnHighlighted =
                hovered !== null &&
                hovered.layer === destLayer &&
                hovered.index === dest.index
              return (
                <g key={`conn-to-${dest.id}`}>
                  {srcNeurons.map((src) => {
                    const b = srcActivation ? srcActivation[src.index] : null
                    const litStyle =
                      b != null
                        ? {
                            stroke: `rgba(255, 255, 255, ${0.1 + 0.8 * b})`,
                            strokeWidth: 0.5 + 1.7 * b,
                          }
                        : undefined
                    return (
                      <line
                        key={`${src.id}-${dest.id}`}
                        x1={src.x}
                        y1={src.y}
                        x2={dest.x}
                        y2={dest.y}
                        className={`nng-conn${isConnHighlighted ? ' highlighted' : ''}`}
                        style={litStyle}
                      />
                    )
                  })}
                </g>
              )
            })}
          </g>
        )
      })}

      {/* 输入样本图片（随步骤出现在输入层左侧） */}
      {showDigit && (
        <foreignObject
          x={digitX}
          y={digitY}
          width={digitSize}
          height={digitSize + 26}
          className="nng-digit-fo"
        >
          <div xmlns="http://www.w3.org/1999/xhtml" className="nng-digit-wrap">
            <MnistDigit key={digitKey} />
            <span className="nng-digit-caption">输入样本</span>
          </div>
        </foreignObject>
      )}

      {/* 神经元 */}
      {neurons.map((layerNeurons, li) => {
        const layerActivation = activations[li]
        return (
          <g key={`neurons-${li}`}>
            {layerNeurons.map((n) => {
              const isSelf =
                hovered !== null &&
                hovered.layer === li &&
                hovered.index === n.index
              const isSource =
                hovered !== null &&
                hovered.layer === li + 1
              const highlighted = isSelf || isSource
              const b = layerActivation ? layerActivation[n.index] : null
              const activeStyle =
                b != null
                  ? {
                      fill: mixColor(b),
                      filter: `drop-shadow(0 0 ${6 * b}px rgba(255, 255, 255, ${0.65 * b}))`,
                    }
                  : undefined
              const labelFill =
                b != null && b > 0.5 ? '#0a0d10' : '#ffffff'
              const showProb = li === outputLayer && softmax
              return (
                <g
                  key={n.id}
                  className={`nng-neuron${highlighted ? ' highlighted' : ''}`}
                  onMouseEnter={() => handleEnter(li, n.index)}
                  onMouseLeave={handleLeave}
                >
                  <circle
                    cx={n.x}
                    cy={n.y}
                    r={highlighted ? neuronR + 3 : neuronR}
                    style={activeStyle}
                  />
                  <text
                    x={n.x}
                    y={n.y + 3.5}
                    className="nng-neuron-label"
                    style={{ fill: labelFill }}
                  >
                    {n.index + 1}
                  </text>
                  {showProb && (
                    <text
                      x={n.x + neuronR + 10}
                      y={n.y + 3.5}
                      className={`nng-prob${n.index === topIndex ? ' top' : ''}`}
                    >
                      {(softmax[n.index] * 100).toFixed(1)}%
                    </text>
                  )}
                </g>
              )
            })}
          </g>
        )
      })}

      {/* 层间双向箭头指示信号流向 */}
      {LAYERS.slice(0, -1).map((_, li) => {
        const x1 = gapX * (li + 1) + 48
        const x2 = gapX * (li + 2) - 48
        const arrowY = 24
        return (
          <g key={`flow-${li}`}>
            <line
              x1={x1}
              y1={arrowY}
              x2={x2}
              y2={arrowY}
              stroke="#2a333d"
              strokeWidth="1.2"
              strokeDasharray="4 3"
            />
            <polygon
              points={`${x2 - 6},${arrowY - 5} ${x2},${arrowY} ${x2 - 6},${arrowY + 5}`}
              fill="#2a333d"
            />
          </g>
        )
      })}
    </svg>
  )
}
