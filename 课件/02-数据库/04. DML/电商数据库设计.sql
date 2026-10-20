-- ============================================
-- 电商数据库设计（演示三种表间关系）
-- 表关系总览：
--   user  ──1:1──→ user_profile    (一对一)
--   category ─1:N─→ product         (一对多)
--   product  ─1:N─→ sku            (一对多)
--   user  ───1:N──→ order           (一对多)
--   order ───M:N─── sku             (多对多, 通过 order_items)
-- ============================================

-- 用户表（主表）
CREATE TABLE "user" (
    id          SERIAL PRIMARY KEY,          -- 用户ID（主键）
    username    VARCHAR(50) UNIQUE NOT NULL,  -- 用户名（唯一）
    email       VARCHAR(100) UNIQUE NOT NULL, -- 邮箱（唯一）
    phone       VARCHAR(20),                  -- 手机号
    created_at  TIMESTAMP DEFAULT NOW()       -- 注册时间
);

-- 用户信息表（从表，与 user 一对一）
CREATE TABLE user_profile (
    id          SERIAL PRIMARY KEY,           -- 信息ID（主键）
    user_id     INTEGER UNIQUE NOT NULL,       -- 关联用户（外键，唯一→一对一）
    full_name   VARCHAR(100),                  -- 真实姓名
    avatar_url  TEXT,                          -- 头像地址
    bio         TEXT,                          -- 个人简介
    birthday    DATE,                          -- 出生日期
    gender      VARCHAR(10),                   -- 性别
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

-- 商品分类表
CREATE TABLE category (
    id          SERIAL PRIMARY KEY,    -- 分类ID（主键）
    name        VARCHAR(50) NOT NULL,  -- 分类名称
    description TEXT                   -- 分类描述
);

-- 商品表（与分类一对多）
CREATE TABLE product (
    id          SERIAL PRIMARY KEY,            -- 商品ID（主键）
    category_id INTEGER NOT NULL,              -- 所属分类（外键→一对多）
    name        VARCHAR(200) NOT NULL,          -- 商品名称
    description TEXT,                           -- 商品描述
    brand       VARCHAR(100),                   -- 品牌
    created_at  TIMESTAMP DEFAULT NOW(),        -- 上架时间
    FOREIGN KEY (category_id) REFERENCES category(id)
);

-- SKU表（与商品一对多）
CREATE TABLE sku (
    id          SERIAL PRIMARY KEY,             -- SKU ID（主键）
    product_id  INTEGER NOT NULL,               -- 所属商品（外键→一对多）
    sku_code    VARCHAR(50) UNIQUE NOT NULL,     -- SKU编码（唯一）
    price       DECIMAL(10,2) NOT NULL,          -- 售价
    stock       INTEGER NOT NULL DEFAULT 0,      -- 库存数量
    attrs       JSONB,                           -- 规格属性（如{"color":"黑色","size":"42"}）
    image_url   TEXT,                            -- 规格图片
    FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE CASCADE
);

-- 订单表（与用户一对多）
CREATE TABLE "order" (
    id           SERIAL PRIMARY KEY,            -- 订单ID（主键）
    user_id      INTEGER NOT NULL,              -- 下单用户（外键→一对多）
    order_no     VARCHAR(50) UNIQUE NOT NULL,   -- 订单编号（唯一）
    status       VARCHAR(20) DEFAULT 'pending', -- 订单状态：pending/paid/shipped/completed/cancelled
    total_amount DECIMAL(10,2),                 -- 订单总金额
    created_at   TIMESTAMP DEFAULT NOW(),       -- 下单时间
    FOREIGN KEY (user_id) REFERENCES "user"(id)
);

-- 订单-商品明细表（中间表，实现 order 与 sku 多对多）
CREATE TABLE order_items (
    order_id    INTEGER NOT NULL,       -- 所属订单（外键）
    sku_id      INTEGER NOT NULL,       -- 购买SKU（外键）
    quantity    INTEGER NOT NULL,        -- 购买数量
    price       DECIMAL(10,2) NOT NULL,  -- 成交单价（快照，不受SKU后续改价影响）
    PRIMARY KEY (order_id, sku_id),     -- 联合主键：一个订单中同种SKU只出现一次
    FOREIGN KEY (order_id) REFERENCES "order"(id) ON DELETE CASCADE,
    FOREIGN KEY (sku_id) REFERENCES sku(id)
);
