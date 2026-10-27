import { forwardRef, useState, useImperativeHandle, useCallback } from 'react';
import './MnistDigit.css';
import mnistImg from '../../assets/mnist_100_digits.png';

// ---------- 切图参数（可微调）----------

/** 左上角第一张子图距离整图左边缘的像素距离 */
const LEFT_EDGE = 106;

/** 左上角第一张子图距离整图上边缘的像素距离 */
const TOP_EDGE = 60;

/** 子图之间的横向间隙（像素） */
const GAP_X = 19.5;

/** 子图之间的纵向间隙（像素） */
const GAP_Y = 5;

/** 每张子图的宽度（像素） */
const CELL_W = 45;

/** 每张子图的高度（像素） */
const CELL_H = 45;

// ---------- 显示缩放 ----------

/** 容器放大倍数 */
const SCALE = 2;

/** 原图尺寸 */
const IMG_W = 812;
const IMG_H = 612;

// ---------- 网格参数 ----------

const GRID_COLS = 10;
const GRID_ROWS = 10;

function getOffset(row, col) {
  const x = LEFT_EDGE + col * (CELL_W + GAP_X);
  const y = TOP_EDGE + row * (CELL_H + GAP_Y);
  return { x, y };
}

const MnistDigit = forwardRef(function MnistDigit({ row, col }, ref) {
  const fixed = row != null && col != null
  const [index, setIndex] = useState(() =>
    Math.floor(Math.random() * GRID_COLS * GRID_ROWS),
  );

  const refresh = useCallback(() => {
    setIndex(Math.floor(Math.random() * GRID_COLS * GRID_ROWS));
  }, []);

  useImperativeHandle(ref, () => ({ refresh }), [refresh]);

  const r = fixed ? row : Math.floor(index / GRID_COLS);
  const c = fixed ? col : index % GRID_COLS;
  const { x, y } = getOffset(r, c);

  return (
    <div
      className="mnist-digit"
      style={{
        width: CELL_W * SCALE,
        height: CELL_H * SCALE,
        backgroundImage: `url(${mnistImg})`,
        backgroundSize: `${IMG_W * SCALE}px ${IMG_H * SCALE}px`,
        backgroundPosition: `-${x * SCALE}px -${y * SCALE}px`,
      }}
    />
  );
});

export default MnistDigit;
