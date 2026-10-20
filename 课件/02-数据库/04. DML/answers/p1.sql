-- ============================================
-- DML 作业答案（第 3 ~ 37 题）
-- ============================================

-- 3. 查询所有商品分类的名称和描述
SELECT name, description FROM category;

-- 4. 查询所有用户的用户名、邮箱和注册时间
SELECT username, email, created_at FROM "user";

-- 5. 查询品牌为"华为"的所有商品
SELECT * FROM product WHERE brand = '华为';

-- 6. 查询价格低于 500 元的 SKU（商品规格）
SELECT * FROM sku WHERE price < 500;

-- 7. 查询库存大于 300 的 SKU
SELECT * FROM sku WHERE stock > 300;

-- 8. 查询 2024 年注册的用户
SELECT * FROM "user" WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01';

-- 9. 查询状态为"completed"的已完成订单
SELECT * FROM "order" WHERE status = 'completed';

-- 10. 查询所有不同的商品品牌
SELECT DISTINCT brand FROM product;

-- 11. 查询所有不同的订单状态
SELECT DISTINCT status FROM "order";

-- 12. 查询最贵的 5 个 SKU
SELECT * FROM sku ORDER BY price DESC LIMIT 5;

-- 13. 查询最新注册的 10 个用户
SELECT * FROM "user" ORDER BY created_at DESC LIMIT 10;

-- 14. 统计用户总数、商品总数、SKU 总数
SELECT
  (SELECT COUNT(*) FROM "user") AS 用户总数,
  (SELECT COUNT(*) FROM product) AS 商品总数,
  (SELECT COUNT(*) FROM sku) AS SKU总数;

-- 15. 计算所有 SKU 的平均价格、最高价和最低价
SELECT
  ROUND(AVG(price)::numeric, 2) AS 平均价格,
  MAX(price) AS 最高价,
  MIN(price) AS 最低价
FROM sku;

-- 16. 统计每个分类下有多少个商品
SELECT c.name AS 分类名称, COUNT(p.id) AS 商品数量
FROM category c
LEFT JOIN product p ON c.id = p.category_id
GROUP BY c.id, c.name;

-- 17. 统计每个品牌的商品数量，只显示商品数超过 2 的品牌
SELECT brand, COUNT(*) AS 商品数量
FROM product
GROUP BY brand
HAVING COUNT(*) > 2;

-- 18. 统计每个用户的订单数量
SELECT u.id, u.username, COUNT(o.id) AS 订单数量
FROM "user" u
LEFT JOIN "order" o ON u.id = o.user_id
GROUP BY u.id, u.username;

-- 19. 统计每个订单状态的数量（pending/paid/shipped/completed/cancelled）
SELECT status, COUNT(*) AS 数量 FROM "order" GROUP BY status;

-- 20. 查询每个商品的平均售价
SELECT p.id, p.name, ROUND(AVG(s.price)::numeric, 2) AS 平均售价
FROM product p
JOIN sku s ON p.id = s.product_id
GROUP BY p.id, p.name;

-- 21. 查询每件商品最便宜的 SKU 价格和最贵的 SKU 价格，以及差价
SELECT p.id, p.name,
       MIN(s.price) AS 最低价,
       MAX(s.price) AS 最高价,
       MAX(s.price) - MIN(s.price) AS 差价
FROM product p
JOIN sku s ON p.id = s.product_id
GROUP BY p.id, p.name;

-- 22. 查询每个分类的商品总库存价值
SELECT c.id, c.name, SUM(s.price * s.stock) AS 总库存价值
FROM category c
JOIN product p ON c.id = p.category_id
JOIN sku s ON p.id = s.product_id
GROUP BY c.id, c.name;

-- 23. 查询商品及其所属分类名称
SELECT p.id, p.name AS 商品名称, c.name AS 分类名称
FROM product p
JOIN category c ON p.category_id = c.id;

-- 24. 查询每个用户及其个人资料信息
SELECT u.id, u.username, up.full_name, up.bio, up.birthday, up.gender
FROM "user" u
LEFT JOIN user_profile up ON u.id = up.user_id;

-- 25. 查询订单明细，显示订单编号、商品名称、SKU 规格、数量、单价，并进行分页，每页10条，显示第3页
SELECT o.order_no, p.name AS 商品名称, s.attrs AS SKU规格, oi.quantity, oi.price
FROM "order" o
JOIN order_items oi ON o.id = oi.order_id
JOIN sku s ON oi.sku_id = s.id
JOIN product p ON s.product_id = p.id
LIMIT 10 OFFSET 20; -- 每页10条，显示第3页（前20条为前两页）

-- 26. 查询每个用户的订单总消费金额，只显示总消费超过 10000 的用户
SELECT u.id, u.username, SUM(o.total_amount) AS 总消费金额
FROM "user" u
JOIN "order" o ON u.id = o.user_id
GROUP BY u.id, u.username
HAVING SUM(o.total_amount) > 10000;

-- 27. 查询哪些商品从未被任何订单购买过
SELECT * FROM product
WHERE id NOT IN (
  SELECT DISTINCT s.product_id
  FROM order_items oi
  JOIN sku s ON oi.sku_id = s.id
);

-- 28. 查询下单次数少于5次的用户
SELECT u.id, u.username, COUNT(o.id) AS 下单次数
FROM "user" u
LEFT JOIN "order" o ON u.id = o.user_id
GROUP BY u.id, u.username
HAVING COUNT(o.id) < 5;

-- 29. 查询购买了"Dell XPS 15"的用户名单
SELECT DISTINCT u.id, u.username, u.email
FROM "user" u
JOIN "order" o ON u.id = o.user_id
JOIN order_items oi ON o.id = oi.order_id
JOIN sku s ON oi.sku_id = s.id
JOIN product p ON s.product_id = p.id
WHERE p.name = 'Dell XPS 15';

-- 30. 查询价格高于所有 SKU 平均价格的 SKU
SELECT * FROM sku
WHERE price > (SELECT AVG(price) FROM sku);

-- 31. 查询下单商品种类最多的前 5 个订单
SELECT o.id, o.order_no, COUNT(oi.sku_id) AS 商品种类数
FROM "order" o
JOIN order_items oi ON o.id = oi.order_id
GROUP BY o.id, o.order_no
ORDER BY COUNT(oi.sku_id) DESC
LIMIT 5;

-- 32. 查询 2024 年各个月份的注册用户数
SELECT EXTRACT(MONTH FROM created_at) AS 月份, COUNT(*) AS 注册人数
FROM "user"
WHERE EXTRACT(YEAR FROM created_at) = 2024
GROUP BY EXTRACT(MONTH FROM created_at)
ORDER BY 月份;

-- 33. 查询每个月的订单数量和总金额
SELECT TO_CHAR(created_at, 'YYYY-MM') AS 月份,
       COUNT(*) AS 订单数量,
       SUM(total_amount) AS 总金额
FROM "order"
GROUP BY TO_CHAR(created_at, 'YYYY-MM')
ORDER BY 月份;

-- 34. 查询用户名包含"hua"的用户
SELECT * FROM "user" WHERE username LIKE '%hua%';

-- 35. 查询 2025 年下单最多的前 3 位用户
SELECT u.id, u.username, COUNT(o.id) AS 下单次数
FROM "user" u
JOIN "order" o ON u.id = o.user_id
WHERE o.created_at >= '2025-01-01' AND o.created_at < '2026-01-01'
GROUP BY u.id, u.username
ORDER BY COUNT(o.id) DESC
LIMIT 3;

