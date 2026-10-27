import { useState, useCallback } from 'react'
import BackpropGraph from './components/BackpropGraph/BackpropGraph.jsx'
import ParamOverlay from './components/ParamOverlay/ParamOverlay.jsx'
import './BackPropagationPage.css'

const LAYER_COUNTS = [8, 16, 16, 10]
const MAX_STEP = 8
const STEP_LABELS = [
  '等待开始',
  '① 显示真实标签',
  '② 计算损失度',
  '③ 对输出层的期望',
  '④ 对隐藏层 2 的期望',
  '④ 对隐藏层 2 的期望',
  '⑤ 对隐藏层 1 的期望',
  '⑤ 对隐藏层 1 的期望',
  '⑥ 更新所有参数',
]

function generateActivations() {
  return LAYER_COUNTS.map((count) =>
    Array.from({ length: count }, () => Math.round(Math.random() * 100) / 100),
  )
}

export default function BackPropagationPage() {
  const [activations] = useState(generateActivations)
  const [step, setStep] = useState(0)

  const handleNext = useCallback(() => {
    setStep((s) => Math.min(s + 1, MAX_STEP))
  }, [])

  const handlePrev = useCallback(() => {
    setStep((s) => Math.max(s - 1, 0))
  }, [])

  const handleReset = useCallback(() => {
    setStep(0)
  }, [])

  return (
    <div className="bpp">
      <div className="bpp-head">
        <div>
          <span className="bpp-eyebrow">BACK PROPAGATION · 反向传播</span>
          <h1>全连接神经网络 — 误差向后流动</h1>
        </div>
        <code className="bpp-formula">
          δ⁽ˡ⁾ = (W⁽ˡ⁺¹⁾)ᵀ δ⁽ˡ⁺¹⁾ ⊙ f′(z⁽ˡ⁾)
        </code>
      </div>
      <div className="bpp-body">
        <div className="bpp-viz">
          <div className="bpp-viz-inner">
            <BackpropGraph activations={activations} step={step} />
          </div>
          {step >= 8 && <ParamOverlay />}
        </div>
        <aside className="bpp-controls">
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
              {Array.from({ length: MAX_STEP }, (_, i) => (
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
