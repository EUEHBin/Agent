import { useState, useCallback, useMemo } from 'react'
import NetworkGraph from './components/NetworkGraph/NetworkGraph.jsx'
import './ForwardPropagationPage.css'

const LAYER_COUNTS = [8, 16, 16, 10]
const MAX_STEP = LAYER_COUNTS.length
const STEP_LABELS = [
  '等待开始',
  '① 输入层点亮',
  '② 隐藏层 1 点亮',
  '③ 隐藏层 2 点亮',
  '④ 输出层点亮',
]

function generateAllActivations() {
  return LAYER_COUNTS.map((count) =>
    Array.from({ length: count }, () => 0.2 + Math.random() * 0.8),
  )
}

export default function ForwardPropagationPage() {
  const [step, setStep] = useState(0)
  const [generated, setGenerated] = useState(null)
  const [digitKey, setDigitKey] = useState(0)

  const handleNext = useCallback(() => {
    if (step >= MAX_STEP) return
    if (!generated) {
      setGenerated(generateAllActivations())
      setDigitKey((k) => k + 1)
    }
    setStep(step + 1)
  }, [step, generated])

  const handlePrev = useCallback(() => {
    if (step <= 0) return
    setStep(step - 1)
  }, [step])

  const handleReset = useCallback(() => {
    setStep(0)
    setGenerated(null)
  }, [])

  const activations = useMemo(
    () =>
      LAYER_COUNTS.map((_, i) =>
        generated && i < step ? generated[i] : null,
      ),
    [generated, step],
  )

  return (
    <div className="fpp">
      <div className="fpp-head">
        <div>
          <span className="fpp-eyebrow">FORWARD PROPAGATION · 前向传播</span>
          <h1>全连接神经网络 — 信号向前流动</h1>
        </div>
        <code className="fpp-formula">
          a⁽ˡ⁾ = f(W⁽ˡ⁾ a⁽ˡ⁻¹⁾ + b⁽ˡ⁾)
        </code>
      </div>
      <div className="fpp-body">
        <div className="fpp-viz">
          <div className="fpp-viz-inner">
            <NetworkGraph
              activations={activations}
              showDigit={step >= 1}
              digitKey={digitKey}
            />
          </div>
        </div>
        <aside className="fpp-controls">
          <section className="ctl-block">
            <div className="ctl-title">
              <span className="dot" />
              操作区
            </div>
            <div className="step-status">
              <span className="step-count">
                STEP {step} / {MAX_STEP}
              </span>
              <span className="step-name">{STEP_LABELS[step]}</span>
            </div>
            <div className="step-track">
              {LAYER_COUNTS.map((_, i) => (
                <span
                  key={i}
                  className={`step-seg${step > i ? ' done' : ''}`}
                />
              ))}
            </div>
            <div className="step-buttons">
              <button
                className="step-btn"
                onClick={handlePrev}
                disabled={step === 0}
              >
                上一步
              </button>
              <button
                className="step-btn primary"
                onClick={handleNext}
                disabled={step === MAX_STEP}
              >
                下一步
              </button>
              <button
                className="step-btn ghost"
                onClick={handleReset}
                disabled={step === 0}
              >
                重置
              </button>
            </div>
          </section>
        </aside>
      </div>
    </div>
  )
}
