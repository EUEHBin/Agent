import { useState, useCallback, useMemo } from 'react';
import './AttentionPage.css';

const ROWS = 4;
const COLS = 6;
const MAX_STEP = 8;
const STEP_LABELS = [
  '初始状态',
  'Q、K、V 线性变换',
  '多头注意力 — 切分',
  'Head 1',
  '注意力得分',
  '掩码',
  'Softmax 归一化',
  '加权输出',
  '多头拼接',
];

function generateMatrix(rows, cols) {
  return Array.from({ length: rows }, () =>
    Array.from({ length: cols }, () => Math.random() * 0.8 - 0.4),
  );
}

function matMul(A, B) {
  const m = A.length;
  const n = A[0].length;
  const p = B[0].length;
  const result = Array.from({ length: m }, () => Array(p).fill(0));
  for (let i = 0; i < m; i++)
    for (let k = 0; k < n; k++)
      for (let j = 0; j < p; j++) result[i][j] += A[i][k] * B[k][j];
  return result;
}

function transpose(M) {
  const rows = M.length;
  const cols = M[0].length;
  return Array.from({ length: cols }, (_, i) =>
    Array.from({ length: rows }, (_, j) => M[j][i]),
  );
}

function softmaxRow(row) {
  const exps = row.map((v) => Math.exp(v));
  const sum = exps.reduce((a, b) => a + b, 0);
  return exps.map((v) => v / sum);
}

function sliceCols(M, start, count) {
  return M.map((row) => row.slice(start, start + count));
}

function formatCell(val) {
  if (val === -Infinity) return '-∞';
  return typeof val === 'number' ? val.toFixed(2) : val;
}

function MatrixView({ matrix, className, cols }) {
  return (
    <div className={`atp-matrix ${className || ''}`}>
      {matrix.map((row, ri) => {
        const cells = cols != null ? row.slice(0, cols) : row;
        return (
          <div key={ri} className="atp-matrix-row">
            {cells.map((val, ci) => (
              <span key={ci} className="atp-matrix-cell">
                {formatCell(val)}
              </span>
            ))}
          </div>
        );
      })}
    </div>
  );
}

export default function AttentionPage() {
  const [step, setStep] = useState(0);

  const embedding = useMemo(() => generateMatrix(ROWS, COLS), []);
  const outputMatrix = useMemo(() => generateMatrix(ROWS, COLS), []);
  const Wq = useMemo(() => generateMatrix(COLS, COLS), []);
  const Wk = useMemo(() => generateMatrix(COLS, COLS), []);
  const Wv = useMemo(() => generateMatrix(COLS, COLS), []);
  const Q = useMemo(() => matMul(embedding, Wq), [embedding, Wq]);
  const K = useMemo(() => matMul(embedding, Wk), [embedding, Wk]);
  const V = useMemo(() => matMul(embedding, Wv), [embedding, Wv]);

  const headCols = COLS / 2;
  const Qh = useMemo(() => sliceCols(Q, 0, headCols), [Q, headCols]);
  const Kh = useMemo(() => sliceCols(K, 0, headCols), [K, headCols]);
  const Vh = useMemo(() => sliceCols(V, 0, headCols), [V, headCols]);

  const Qh2 = useMemo(() => sliceCols(Q, headCols, headCols), [Q, headCols]);
  const Kh2 = useMemo(() => sliceCols(K, headCols, headCols), [K, headCols]);
  const Vh2 = useMemo(() => sliceCols(V, headCols, headCols), [V, headCols]);
  const attentionScores = useMemo(() => {
    const raw = matMul(Qh, transpose(Kh));
    return raw.map((row) => row.map((v) => v * 100));
  }, [Qh, Kh]);

  const maskedScores = useMemo(
    () =>
      attentionScores.map((row, i) =>
        row.map((v, j) => (j > i ? -Infinity : v)),
      ),
    [attentionScores],
  );

  const softmaxScores = useMemo(
    () => maskedScores.map((row) => softmaxRow(row)),
    [maskedScores],
  );

  const headOutput = useMemo(
    () => matMul(softmaxScores, Vh),
    [softmaxScores, Vh],
  );

  const attentionScores2 = useMemo(() => {
    const raw = matMul(Qh2, transpose(Kh2));
    return raw.map((row) => row.map((v) => v * 100));
  }, [Qh2, Kh2]);

  const maskedScores2 = useMemo(
    () =>
      attentionScores2.map((row, i) =>
        row.map((v, j) => (j > i ? -Infinity : v)),
      ),
    [attentionScores2],
  );

  const softmaxScores2 = useMemo(
    () => maskedScores2.map((row) => softmaxRow(row)),
    [maskedScores2],
  );

  const head2Output = useMemo(
    () => matMul(softmaxScores2, Vh2),
    [softmaxScores2, Vh2],
  );

  const multiHeadOutput = useMemo(
    () => headOutput.map((row, i) => [...row, ...head2Output[i]]),
    [headOutput, head2Output],
  );

  const handleNext = useCallback(() => {
    setStep((s) => Math.min(s + 1, MAX_STEP));
  }, []);

  const handlePrev = useCallback(() => {
    setStep((s) => Math.max(s - 1, 0));
  }, []);

  const handleReset = useCallback(() => {
    setStep(0);
  }, []);

  return (
    <div className="atp">
      <div className="atp-head">
        <div>
          <span className="atp-eyebrow">SELF-ATTENTION · 注意力机制</span>
          <h1>Transformer 前向传播 — 自注意力</h1>
        </div>
        <code className="atp-formula">
          Attention(Q, K, V) = softmax(QK<sup>T</sup> / √d<sub>k</sub>)V
        </code>
      </div>

      <div className="atp-body">
        <div className="atp-viz">
          <div className="atp-flow">
            {/* 嵌入结果矩阵 - 始终显示 */}
            <div className="atp-matrix-block">
              <span className="atp-block-label">嵌入结果 X</span>
              <MatrixView matrix={embedding} />
              <span className="atp-shape">
                {ROWS} × {COLS}
              </span>
            </div>

            {/* 箭头 - step < 7 时显示 */}
            {step < 7 && (
              <div className="atp-arrow-wrap">
                <span className="atp-arrow-text">→</span>
              </div>
            )}

            {/* Step >= 3 && step < 7: Head 1 标签 */}
            {step >= 3 && step < 7 && (
              <span className="atp-head-label">Head 1</span>
            )}

            {/* Step 0: 注意力层 + 结果 */}
            {step === 0 && (
              <>
                <div className="atp-attention-block">
                  <span className="atp-block-label">注意力层</span>
                  <div className="atp-attention-box">
                    <span className="atp-attention-question">?</span>
                  </div>
                </div>

                <div className="atp-arrow-wrap">
                  <span className="atp-arrow-text">→</span>
                </div>

                <div className="atp-matrix-block">
                  <span className="atp-block-label">如何调整</span>
                  <MatrixView
                    matrix={outputMatrix}
                    className="atp-matrix-output"
                  />
                  <span className="atp-shape">
                    {ROWS} × {COLS}
                  </span>
                </div>
              </>
            )}

            {/* Step >= 1 && step < 7: Q/K/V 线性变换 */}
            {step >= 1 && step < 7 && (
              <div className="atp-qkv-col">
                {step < 7 && (
                  <div className="atp-qkv-branch">
                    {step < 3 && (
                      <span
                        className={`atp-weight-group${step >= 2 ? ' atp-fade-out' : ''}`}
                      >
                        <span className="atp-op">×</span>
                        <span className="atp-weight-label">
                          W<sub>Q</sub>{' '}
                          <span className="atp-weight-shape">(6×6)</span>
                        </span>
                        <span className="atp-op">=</span>
                      </span>
                    )}
                    <div className="atp-matrix-block">
                      <span className="atp-block-label atp-label-q atp-label-left">
                        Q: Query，我怎么去找别人？
                      </span>
                      <div className="atp-matrix-container">
                        <MatrixView
                          matrix={Q}
                          className="atp-matrix-q"
                          cols={step >= 3 ? COLS / 2 : undefined}
                        />
                        {step === 2 && (
                          <div className="atp-divider atp-divider-q" />
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {step < 7 && (
                  <div className="atp-qkv-branch">
                    {step < 3 && (
                      <span
                        className={`atp-weight-group${step >= 2 ? ' atp-fade-out' : ''}`}
                      >
                        <span className="atp-op">×</span>
                        <span className="atp-weight-label">
                          W<sub>K</sub>{' '}
                          <span className="atp-weight-shape">(6×6)</span>
                        </span>
                        <span className="atp-op">=</span>
                      </span>
                    )}
                    <div className="atp-matrix-block">
                      <span className="atp-block-label atp-label-k atp-label-left">
                        K: Key，别人怎么找到我？
                      </span>
                      <div className="atp-matrix-container">
                        <MatrixView
                          matrix={K}
                          className="atp-matrix-k"
                          cols={step >= 3 ? COLS / 2 : undefined}
                        />
                        {step === 2 && (
                          <div className="atp-divider atp-divider-k" />
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {step < 4 && (
                  <div className="atp-qkv-branch">
                    {step < 3 && (
                      <span
                        className={`atp-weight-group${step >= 2 ? ' atp-fade-out' : ''}`}
                      >
                        <span className="atp-op">×</span>
                        <span className="atp-weight-label">
                          W<sub>V</sub>{' '}
                          <span className="atp-weight-shape">(6×6)</span>
                        </span>
                        <span className="atp-op">=</span>
                      </span>
                    )}
                    <div className="atp-matrix-block">
                      <span className="atp-block-label atp-label-v atp-label-left">
                        V: Value，我找到别人后，对它施加怎样的影响？
                      </span>
                      <div className="atp-matrix-container">
                        <MatrixView
                          matrix={V}
                          className="atp-matrix-v"
                          cols={step >= 3 ? COLS / 2 : undefined}
                        />
                        {step === 2 && (
                          <div className="atp-divider atp-divider-v" />
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Step >= 4 && step < 8: 注意力得分 */}
            {step >= 4 && step < 8 && (
              <>
                <div className="atp-arrow-wrap">
                  <span className="atp-arrow-text">→</span>
                </div>
                <div className="atp-matrix-block">
                  <span className="atp-block-label atp-label-score atp-label-left">
                    注意力得分: Q × K<sup>T</sup>
                    {step >= 6 && (
                      <span className="atp-softmax-label"> → Softmax</span>
                    )}
                  </span>
                  <MatrixView
                    matrix={
                      step >= 6
                        ? softmaxScores
                        : step >= 5
                          ? maskedScores
                          : attentionScores
                    }
                    className="atp-matrix-score"
                  />
                  <span className="atp-shape">
                    {attentionScores.length} × {attentionScores[0].length}
                  </span>
                </div>
              </>
            )}

            {/* Step >= 7 && step < 8: 加权输出 */}
            {step >= 7 && step < 8 && (
              <>
                <div className="atp-arrow-wrap">
                  <span className="atp-arrow-text">→</span>
                </div>
                <span className="atp-weight-label">× V</span>
                <div className="atp-arrow-wrap">
                  <span className="atp-arrow-text">=</span>
                </div>
                <div className="atp-matrix-block">
                  <span className="atp-block-label atp-label-v atp-label-left">
                    Head 1
                  </span>
                  <MatrixView matrix={headOutput} className="atp-matrix-v" />
                  <span className="atp-shape">
                    {headOutput.length} × {headOutput[0].length}
                  </span>
                </div>
              </>
            )}

            {/* Step >= 8: 多头拼接 */}
            {step >= 8 && (
              <>
                <div className="atp-arrow-wrap">
                  <span className="atp-arrow-text">→</span>
                </div>
                <div className="atp-multihead-col">
                  <div className="atp-multihead-row">
                    <div className="atp-matrix-block">
                      <span className="atp-block-label atp-label-v atp-label-left">
                        Head 1
                      </span>
                      <MatrixView
                        matrix={headOutput}
                        className="atp-matrix-v"
                      />
                    </div>
                    <div className="atp-matrix-block">
                      <span className="atp-block-label atp-label-v atp-label-left">
                        Head 2
                      </span>
                      <MatrixView
                        matrix={head2Output}
                        className="atp-matrix-v"
                      />
                    </div>
                  </div>
                  <div className="atp-arrow-wrap atp-arrow-down">
                    <span className="atp-arrow-text">↓</span>
                  </div>
                  <div className="atp-matrix-block">
                    <span className="atp-block-label atp-label-score atp-label-left">
                      MultiHead
                    </span>
                    <MatrixView
                      matrix={multiHeadOutput}
                      className="atp-matrix-score"
                    />
                    <span className="atp-shape">
                      {multiHeadOutput.length} × {multiHeadOutput[0].length}
                    </span>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>

        <aside className="atp-controls">
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
  );
}
