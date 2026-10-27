export const relu = (x) => Math.max(0, x)

export const sigmoid = (x) => 1 / (1 + Math.exp(-x))

/**
 * 单个神经元前向计算
 * 亮度归一化使用 tanh：y=0（未激活）→ 0 纯黑；y 越大 → 越接近 1 纯白
 * @param {number[]} values  已归一化的输入值
 * @param {number[]} weights 权重（与 values 等长）
 * @param {number} bias      偏置
 * @returns {{ z: number, y: number, norm: number, contribs: number[] }}
 */
export function computeNeuron(values, weights, bias) {
  const contribs = values.map((v, i) => v * (weights[i] ?? 0))
  const z = contribs.reduce((s, c) => s + c, 0) + bias
  const y = relu(z)
  return { z, y, norm: Math.tanh(y), contribs }
}
