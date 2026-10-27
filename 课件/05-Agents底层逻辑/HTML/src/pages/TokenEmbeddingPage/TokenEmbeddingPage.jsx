import { useState, useMemo } from 'react';
import './TokenEmbeddingPage.css';

const TOKENS = ['你', '是', '谁', '？'];
const TOKEN_IDS = ['101', '872', '6443', '136'];
const DIM = 768;
const VOCAB = 30522;

const EMBED_TOP_ROWS = [
  ['0.02', '-0.14', '0.33', '0.21', '-0.07'],
  ['0.11', '0.52', '-0.21', '-0.09', '0.18'],
];
const EMBED_BOTTOM_ROWS = [['-0.05', '0.31', '-0.17', '0.44', '-0.02']];

export default function TokenEmbeddingPage() {
  const [activeSet, setActiveSet] = useState(new Set());

  const handleStageClick = (index) => {
    setActiveSet((prev) => {
      const next = new Set(prev);
      if (next.has(index)) {
        next.delete(index);
      } else {
        next.add(index);
      }
      return next;
    });
  };

  const outputRows = useMemo(
    () =>
      Array.from({ length: 4 }, () =>
        Array.from({ length: 4 }, () => (Math.random() * 1.2 - 0.6).toFixed(2)),
      ),
    [],
  );

  return (
    <div className="tep">
      <div className="tep-head">
        <div>
          <span className="tep-eyebrow">TOKEN EMBEDDING · 词嵌入</span>
          <h1>Transformer 前向传播 — 第一阶段：词嵌入</h1>
        </div>
        <code className="tep-formula">
          X<sub>embed</sub> = W<sub>e</sub>[token_ids] ∈ ℝ<sup>n × d</sup>
        </code>
      </div>

      <div className="tep-body">
        <div className="tep-viz">
          <div className="tep-flow">
            {/* ========== Stage 1: 输入文本 ========== */}
            <div className="tep-stage">
              <div
                className={`tep-stage-inner${activeSet.has(0) ? ' active' : ''}`}
                onClick={() => handleStageClick(0)}
              >
                <span className="tep-stage-title">输入</span>
                <div className="tep-block tep-text-block">
                  {TOKENS.map((ch, i) => (
                    <div key={i} className="tep-char-cell">
                      {ch}
                    </div>
                  ))}
                </div>
                <span className="tep-dim"></span>
              </div>
            </div>

            {/* ========== Arrow: 分词器 ========== */}
            <div className="tep-arrow-wrap">
              <span className="tep-arrow">→</span>
              <span className="tep-arrow-note">分词器</span>
            </div>

            {/* ========== Stage 2: Token IDs (4×1) ========== */}
            <div className="tep-stage">
              <div
                className={`tep-stage-inner${activeSet.has(1) ? ' active' : ''}`}
                onClick={() => handleStageClick(1)}
              >
                <span className="tep-stage-title">Tokens</span>
                <div className="tep-block tep-card tep-tilt">
                  <div className="tep-ids-col">
                    {TOKEN_IDS.map((id, i) => (
                      <div key={i} className="tep-id-cell">
                        {id}
                      </div>
                    ))}
                  </div>
                </div>
                <span className="tep-dim">4 × 1</span>
              </div>
            </div>

            {/* ========== Arrow ========== */}
            <div className="tep-arrow-wrap">
              <span className="tep-arrow">→</span>
            </div>

            {/* ========== Stage 3: Embedding Layer ========== */}
            <div className="tep-stage">
              <div
                className={`tep-stage-inner${activeSet.has(2) ? ' active' : ''}`}
                onClick={() => handleStageClick(2)}
              >
                <span className="tep-stage-title">Embedding Layer</span>
                <div className="tep-block tep-card tep-tilt tep-embed-card">
                  <div className="tep-embed-matrix">
                    {EMBED_TOP_ROWS.map((row, ri) => (
                      <div key={`t${ri}`} className="tep-embed-row">
                        {row.map((val, ci) => (
                          <span key={ci} className="tep-embed-cell">
                            {val}
                          </span>
                        ))}
                        <span className="tep-embed-dots">···</span>
                        <span className="tep-embed-cell">
                          {['0.18', '-0.11'][ri]}
                        </span>
                      </div>
                    ))}
                    <div className="tep-embed-row">
                      <span className="tep-embed-cell">0.41</span>
                      <span className="tep-embed-cell">-0.03</span>
                      <span className="tep-embed-cell">0.27</span>
                      <span className="tep-embed-cell">-0.19</span>
                      <span className="tep-embed-cell">0.35</span>
                      <span className="tep-embed-dots">···</span>
                      <span className="tep-embed-cell">0.52</span>
                    </div>
                    <div className="tep-embed-ellipsis">
                      {Array.from({ length: 5 }, (_, i) => (
                        <span key={i} className="tep-dot-row">
                          ·
                        </span>
                      ))}
                    </div>
                    {EMBED_BOTTOM_ROWS.map((row, ri) => (
                      <div key={`b${ri}`} className="tep-embed-row">
                        {row.map((val, ci) => (
                          <span key={ci} className="tep-embed-cell">
                            {val}
                          </span>
                        ))}
                        <span className="tep-embed-dots">···</span>
                        <span className="tep-embed-cell">0.07</span>
                      </div>
                    ))}
                  </div>
                </div>
                <span className="tep-dim">
                  {VOCAB.toLocaleString()} × {DIM}
                </span>
              </div>
            </div>

            {/* ========== Arrow ========== */}
            <div className="tep-arrow-wrap">
              <span className="tep-arrow">→</span>
            </div>

            {/* ========== Stage 4: Output (4×768) ========== */}
            <div className="tep-stage">
              <div
                className={`tep-stage-inner${activeSet.has(3) ? ' active' : ''}`}
                onClick={() => handleStageClick(3)}
              >
                <span className="tep-stage-title">Output</span>
                <div className="tep-block tep-card tep-tilt tep-output-card">
                  <div className="tep-output-matrix">
                    {outputRows.map((row, i) => (
                      <div key={i} className="tep-embed-row">
                        {row.slice(0, 3).map((val, ci) => (
                          <span key={ci} className="tep-embed-cell">{val}</span>
                        ))}
                        <span className="tep-embed-dots">···</span>
                        <span className="tep-embed-cell">{row[3]}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <span className="tep-dim">4 × {DIM}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
