BEGIN;

-- ============================================================
-- 分类数据
-- ============================================================
INSERT INTO category (id, name, description) OVERRIDING SYSTEM VALUE VALUES
(1, '智能手机', '各品牌旗舰及主流智能手机'),
(2, '笔记本电脑', '轻薄本、商务本与游戏本'),
(3, '平板电脑', 'iPad、安卓及鸿蒙平板'),
(4, '耳机/音频设备', '无线耳机、头戴式耳机与真无线耳机'),
(5, '智能手表/可穿戴设备', '智能手表与运动手表'),
(6, '游戏主机/掌机', '家用游戏主机与掌上游戏机')
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 产品数据
-- ============================================================
INSERT INTO product (id, name, description, brand) OVERRIDING SYSTEM VALUE VALUES

-- 智能手机 (category 1)
(1, 'iPhone 16 Pro Max',
 '中国大陆以外地区称 iPhone 16 Pro Max。Apple 于2024年9月发布的旗舰智能手机，搭载 A18 Pro 芯片、6.9 英寸超视网膜 XDR 显示屏、4800 万像素融合式摄像头系统，支持 Apple Intelligence。',
 'Apple'),

(2, 'iPhone 16',
 'Apple 于2024年9月发布的次旗舰智能手机，搭载 A18 芯片、6.1 英寸超视网膜 XDR 显示屏、4800 万像素融合式摄像头，新增相机控制按钮，支持 Apple Intelligence。',
 'Apple'),

(3, 'Samsung Galaxy S25 Ultra',
 'Samsung 于2025年1月发布的旗舰智能手机，搭载骁龙 8 Elite for Galaxy 芯片、6.9 英寸 Dynamic AMOLED 2X 显示屏、2 亿像素主摄，内置 S Pen，采用钛金属框架。',
 'Samsung'),

(4, 'Xiaomi 15 Pro',
 '小米于2024年10月发布的旗舰智能手机，首发搭载骁龙 8 Elite 芯片、6.73 英寸 2K LTPO 微曲屏、徕卡光学 Summilux 镜头，预装 HyperOS 2 系统。',
 'Xiaomi'),

(5, 'Huawei Pura 70 Ultra',
 '华为于2024年4月发布的影像旗舰手机，搭载麒麟 9010 芯片、6.8 英寸 LTPO OLED 屏、超聚光伸缩摄像头（1 英寸传感器），支持北斗卫星图片消息。',
 'Huawei'),

(6, 'Google Pixel 9 Pro',
 'Google 于2024年8月发布的旗舰智能手机，搭载 Tensor G4 芯片、6.3 英寸 Super Actua OLED 屏、新一代 AI 影像系统，预装纯净 Android 14，支持 Gemini 高级 AI 功能。',
 'Google'),

-- 笔记本电脑 (category 2)
(7, 'MacBook Pro 16 英寸 (M4 Pro)',
 'Apple 于2024年10月发布的高性能笔记本电脑，搭载 M4 Pro 或 M4 Max 芯片、16 英寸 Liquid Retina XDR 显示屏、最长 24 小时电池续航，配备雷雳 5 接口，专为专业创意工作流打造。',
 'Apple'),

(8, 'MacBook Air 15 英寸 (M4)',
 'Apple 于2025年3月发布的轻薄笔记本电脑，搭载 M4 芯片、15.3 英寸 Liquid Retina 显示屏、无风扇静音设计，起售价较上代下调。',
 'Apple'),

(9, 'ThinkPad X1 Carbon Gen 12',
 '联想于2024年发布的旗舰商务超极本，搭载全新 Intel Core Ultra 处理器、14 英寸 2.8K OLED 屏、镁合金机身仅重 1.09kg，通过 MIL-STD-810H 军标认证。',
 'Lenovo'),

(10, 'Dell XPS 16',
 'Dell 于2024年发布的大屏性能本，搭载 Intel Core Ultra 处理器、16.3 英寸 4K OLED 触控屏、极窄边框设计，采用 CNC 铝合金机身与无缝玻璃触控板。',
 'Dell'),

(11, 'ROG Zephyrus G16 (2024)',
 '华硕 ROG 于2024年发布的轻薄游戏本，最高搭载 Intel Core Ultra 9 与 RTX 4090、16 英寸 2.5K 240Hz OLED 星云原画屏、铝合金机身仅重 1.85kg。',
 'ASUS'),

(12, 'Surface Laptop 7',
 '微软于2024年发布的 AI PC，搭载骁龙 X Elite 芯片、13.8 英寸 PixelSense 触控屏、内置 NPU 提供每秒 45 万亿次算力，预装 Windows 11 并深度集成 Copilot。',
 'Microsoft'),

-- 平板电脑 (category 3)
(13, 'iPad Pro 13 英寸 (M4)',
 'Apple 于2024年5月发布的旗舰平板，搭载 M4 芯片、13 英寸 Ultra Retina XDR 双层串联 OLED 屏、厚度仅 5.1mm 为 Apple 迄今最薄产品，支持全新 Apple Pencil Pro。',
 'Apple'),

(14, 'iPad Air 11 英寸 (M3)',
 'Apple 于2025年3月发布的性能平板，搭载 M3 芯片、11 英寸 Liquid Retina 显示屏，支持 Apple Pencil Pro 与妙控键盘，提供 4 色可选。',
 'Apple'),

(15, 'Samsung Galaxy Tab S10 Ultra',
 'Samsung 于2024年9月发布的旗舰安卓平板，搭载天玑 9300+ 芯片、14.6 英寸 Dynamic AMOLED 2X 显示屏、120Hz 刷新率，支持 S Pen，内置 Galaxy AI。',
 'Samsung'),

(16, 'Xiaomi Pad 7 Pro',
 '小米于2024年10月发布的性能平板，搭载骁龙 8s Gen 3 芯片、11.2 英寸 3.2K 144Hz LCD 屏、8850mAh 大电池，预装 HyperOS 2，支持小米焦点触控笔。',
 'Xiaomi'),

(17, 'Huawei MatePad Pro 13.2 (2024)',
 '华为于2024年11月发布的旗舰鸿蒙平板，搭载麒麟 9020 W 芯片、13.2 英寸 OLED 柔性屏，支持天生会画 App 与第三代 M-Pencil，运行 HarmonyOS NEXT。',
 'Huawei'),

-- 耳机/音频设备 (category 4)
(18, 'AirPods Pro 2',
 'Apple 于2022年9月发布并在后续通过软件升级的真无线降噪耳机，搭载 H2 芯片、自适应降噪与通透模式，支持 USB-C 充电，后续更新加入临床级助听器功能。',
 'Apple'),

(19, 'AirPods Max',
 'Apple 于2020年12月发布并在2024年更新为 USB-C 接口的头戴式降噪耳机，搭载 H1 芯片、高保真音频、自适应均衡与空间音频，五种配色。',
 'Apple'),

(20, 'Sony WH-1000XM6',
 'Sony 于2025年发布的旗舰头戴式无线降噪耳机，搭载集成处理器 V2+QN2e、自适应声音控制、LDAC 高解析音频传输，续航 40 小时。',
 'Sony'),

(21, 'Bose QuietComfort Ultra Headphones',
 'Bose 于2023年发布的旗舰头戴式降噪耳机，搭载 CustomTune 智能耳内音场调校、沉浸空间音频技术，支持 Snapdragon Sound 骁龙畅听。',
 'Bose'),

(22, 'Samsung Galaxy Buds3 Pro',
 'Samsung 于2024年7月发布的真无线降噪耳机，带柄式设计、双功放扬声器、自适应 ANC，支持 Galaxy AI 实时翻译与 360 空间音频。',
 'Samsung'),

(23, 'Sony WF-1000XM6',
 'Sony 于2025年发布的真无线降噪旗舰耳机，搭载集成处理器 V2+QN2e、全新 Dynamic Driver X 动圈单元，降噪与音质全面提升。',
 'Sony'),

-- 智能手表/可穿戴设备 (category 5)
(24, 'Apple Watch Ultra 3',
 'Apple 于2024年9月发布的旗舰运动手表，49mm 钛金属表壳、精准双频 GPS、2000 尼特亮度显示屏，支持水深检测、潜水电脑模式及警笛功能。',
 'Apple'),

(25, 'Apple Watch Series 10',
 'Apple 于2024年9月发布的智能手表，有史以来最薄的 Apple Watch，采用 S10 SiP 芯片、更大宽高比广视角 OLED 屏，新增睡眠呼吸暂停检测功能。',
 'Apple'),

(26, 'Samsung Galaxy Watch7 Ultra',
 'Samsung 于2024年7月发布的旗舰安卓智能手表，47mm 钛金属表壳、Exynos W1000 3nm 芯片、BioActive 传感器，支持 Galaxy AI 健康洞察。',
 'Samsung'),

(27, 'Huawei Watch GT 5 Pro',
 '华为于2024年9月发布的旗舰智能手表，46mm/42mm 钛合金表壳、TruSense 系统、向日葵定位天线 2.0，支持 100 余种运动模式与 ECG 心电图分析。',
 'Huawei'),

(28, 'Garmin Fenix 8',
 'Garmin 于2024年8月发布的旗舰户外运动手表，提供 AMOLED 与太阳能充电版，多频多星定位、LED 手电筒，支持卫星消息和离线地图。',
 'Garmin'),

-- 游戏主机/掌机 (category 6)
(29, 'Nintendo Switch OLED',
 '任天堂于2021年10月发布的掌机/家用混合游戏机，7 英寸 OLED 屏、64GB 内置存储、宽幅可调支架，兼容全部 Switch 游戏库。',
 'Nintendo'),

(30, 'PlayStation 5 Pro',
 'Sony 于2024年11月发布的高性能游戏主机，搭载更强 GPU（RDNA 架构光线追踪）、AI 驱动 PlayStation Spectral Super Resolution 超分技术、2TB 固态硬盘。',
 'Sony'),

(31, 'Xbox Series X (2024)',
 '微软于2024年10月推出的 Xbox Series X 数字版，取消光驱但提供 2TB 固态硬盘，支持 Xbox Game Pass Ultimate 云游戏服务与向后兼容。',
 'Microsoft'),

(32, 'Steam Deck OLED',
 'Valve 于2023年11月发布的掌上游戏 PC，7.4 英寸 HDR OLED 屏、AMD 定制 APU、SteamOS 系统，可流畅运行 Steam 库中大多数 3A 游戏。',
 'Valve')

ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 产品-分类关联数据
-- ============================================================
INSERT INTO product_category (product_id, category_id) VALUES
-- 智能手机
(1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1),
-- 笔记本电脑
(7, 2), (8, 2), (9, 2), (10, 2), (11, 2), (12, 2),
-- 平板电脑
(13, 3), (14, 3), (15, 3), (16, 3), (17, 3),
-- 耳机/音频设备
(18, 4), (19, 4), (20, 4), (21, 4), (22, 4), (23, 4),
-- 智能手表/可穿戴设备
(24, 5), (25, 5), (26, 5), (27, 5), (28, 5),
-- 游戏主机/掌机
(29, 6), (30, 6), (31, 6), (32, 6)
ON CONFLICT (product_id, category_id) DO NOTHING;

-- ============================================================
-- SKU 数据
-- ============================================================
INSERT INTO sku (id, product_id, sku_code, price, stock, attrs, image_url) OVERRIDING SYSTEM VALUE VALUES

-- iPhone 16 Pro Max
(1, 1, 'IP16PM-256-TIBK', 9999.00, 150, '{"颜色": "黑色钛金属", "存储": "256GB"}', 'https://img.example.com/sku/iphone16promax-black.png'),
(2, 1, 'IP16PM-512-TINT', 11499.00, 120, '{"颜色": "原色钛金属", "存储": "512GB"}', 'https://img.example.com/sku/iphone16promax-natural.png'),
(3, 1, 'IP16PM-1TB-TIWT', 13499.00, 60, '{"颜色": "白色钛金属", "存储": "1TB"}', 'https://img.example.com/sku/iphone16promax-white.png'),

-- iPhone 16
(4, 2, 'IP16-128-BK', 5999.00, 200, '{"颜色": "黑色", "存储": "128GB"}', 'https://img.example.com/sku/iphone16-black.png'),
(5, 2, 'IP16-256-WT', 6999.00, 180, '{"颜色": "白色", "存储": "256GB"}', 'https://img.example.com/sku/iphone16-white.png'),

-- Samsung Galaxy S25 Ultra
(6, 3, 'SGS25U-256-TIBK', 9699.00, 100, '{"颜色": "钛影黑", "存储": "256GB"}', 'https://img.example.com/sku/s25ultra-black.png'),
(7, 3, 'SGS25U-512-TISL', 10699.00, 80, '{"颜色": "钛辉银", "存储": "512GB"}', 'https://img.example.com/sku/s25ultra-silver.png'),

-- Xiaomi 15 Pro
(8, 4, 'MI15P-256-BK', 5299.00, 300, '{"颜色": "黑色", "存储": "256GB"}', 'https://img.example.com/sku/mi15pro-black.png'),
(9, 4, 'MI15P-512-WT', 5899.00, 250, '{"颜色": "白色", "存储": "512GB"}', 'https://img.example.com/sku/mi15pro-white.png'),

-- Huawei Pura 70 Ultra
(10, 5, 'HWP70U-512-BK', 8999.00, 120, '{"颜色": "星芒黑", "存储": "512GB"}', 'https://img.example.com/sku/pura70ultra-black.png'),
(11, 5, 'HWP70U-1TB-GN', 9999.00, 60, '{"颜色": "香颂绿", "存储": "1TB"}', 'https://img.example.com/sku/pura70ultra-green.png'),

-- Google Pixel 9 Pro
(12, 6, 'PIX9P-256-BK', 6999.00, 80, '{"颜色": "曜石黑", "存储": "256GB"}', 'https://img.example.com/sku/pixel9pro-black.png'),
(13, 6, 'PIX9P-512-WT', 7999.00, 50, '{"颜色": "陶瓷白", "存储": "512GB"}', 'https://img.example.com/sku/pixel9pro-white.png'),

-- MacBook Pro 16" M4 Pro
(14, 7, 'MBP16-M4P-24-512-BK', 19999.00, 90, '{"颜色": "深空黑", "芯片": "M4 Pro", "内存": "24GB", "存储": "512GB"}', 'https://img.example.com/sku/mbp16-m4pro-black.png'),
(15, 7, 'MBP16-M4M-36-1TB-SL', 24999.00, 50, '{"颜色": "银色", "芯片": "M4 Max", "内存": "36GB", "存储": "1TB"}', 'https://img.example.com/sku/mbp16-m4max-silver.png'),

-- MacBook Air 15" M4
(16, 8, 'MBA15-M4-16-256-GY', 9499.00, 150, '{"颜色": "深空灰", "芯片": "M4", "内存": "16GB", "存储": "256GB"}', 'https://img.example.com/sku/mba15-m4-gray.png'),
(17, 8, 'MBA15-M4-24-512-MN', 10999.00, 100, '{"颜色": "午夜色", "芯片": "M4", "内存": "24GB", "存储": "512GB"}', 'https://img.example.com/sku/mba15-m4-midnight.png'),

-- ThinkPad X1 Carbon Gen 12
(18, 9, 'TPX1C12-I7-32-1TB-BK', 13999.00, 70, '{"颜色": "黑色", "CPU": "Intel Core Ultra 7", "内存": "32GB", "存储": "1TB"}', 'https://img.example.com/sku/x1carbon12-black.png'),
(19, 9, 'TPX1C12-I7-16-512-BK', 10999.00, 90, '{"颜色": "黑色", "CPU": "Intel Core Ultra 5", "内存": "16GB", "存储": "512GB"}', 'https://img.example.com/sku/x1carbon12-base-black.png'),

-- Dell XPS 16
(20, 10, 'XPS16-I7-16-512-SL', 12999.00, 60, '{"颜色": "铂金银", "CPU": "Intel Core Ultra 7", "内存": "16GB", "存储": "512GB"}', 'https://img.example.com/sku/xps16-silver.png'),

-- ROG Zephyrus G16
(21, 11, 'ROGG16-I9-4070-32-1TB-GY', 14999.00, 50, '{"颜色": "日蚀灰", "CPU": "Intel Core Ultra 9", "显卡": "RTX 4070", "内存": "32GB", "存储": "1TB"}', 'https://img.example.com/sku/zephyrusg16-gray.png'),

-- Surface Laptop 7
(22, 12, 'SL7-SXE-16-512-PL', 11888.00, 80, '{"颜色": "铂金", "芯片": "Snapdragon X Elite", "内存": "16GB", "存储": "512GB"}', 'https://img.example.com/sku/surfacelaptop7-platinum.png'),
(23, 12, 'SL7-SXP-16-256-BK', 9888.00, 100, '{"颜色": "黑色", "芯片": "Snapdragon X Plus", "内存": "16GB", "存储": "256GB"}', 'https://img.example.com/sku/surfacelaptop7-black.png'),

-- iPad Pro 13" M4
(24, 13, 'IPDPRO13-256-WIFI-BK', 9299.00, 110, '{"颜色": "深空黑", "存储": "256GB", "网络": "WiFi"}', 'https://img.example.com/sku/ipadpro13-black.png'),
(25, 13, 'IPDPRO13-512-CELL-SL', 10799.00, 70, '{"颜色": "银色", "存储": "512GB", "网络": "WiFi+蜂窝"}', 'https://img.example.com/sku/ipadpro13-silver-cellular.png'),

-- iPad Air 11" M3
(26, 14, 'IPDAIR11-128-WIFI-GY', 4799.00, 180, '{"颜色": "深空灰", "存储": "128GB", "网络": "WiFi"}', 'https://img.example.com/sku/ipadair11-gray.png'),
(27, 14, 'IPDAIR11-256-WIFI-BL', 5599.00, 150, '{"颜色": "蓝色", "存储": "256GB", "网络": "WiFi"}', 'https://img.example.com/sku/ipadair11-blue.png'),

-- Samsung Galaxy Tab S10 Ultra
(28, 15, 'SGT10U-256-WIFI-GY', 8999.00, 60, '{"颜色": "石墨灰", "存储": "256GB", "网络": "WiFi"}', 'https://img.example.com/sku/tabs10ultra-gray.png'),

-- Xiaomi Pad 7 Pro
(29, 16, 'MIPAD7P-128-WIFI-BK', 3299.00, 200, '{"颜色": "黑色", "存储": "128GB", "网络": "WiFi"}', 'https://img.example.com/sku/mipad7pro-black.png'),
(30, 16, 'MIPAD7P-256-WIFI-GN', 3799.00, 170, '{"颜色": "绿色", "存储": "256GB", "网络": "WiFi"}', 'https://img.example.com/sku/mipad7pro-green.png'),

-- Huawei MatePad Pro 13.2
(31, 17, 'HWMPP132-256-WIFI-BK', 6999.00, 90, '{"颜色": "曜金黑", "存储": "256GB", "网络": "WiFi"}', 'https://img.example.com/sku/matepadpro132-black.png'),
(32, 17, 'HWMPP132-512-WIFI-WT', 7999.00, 60, '{"颜色": "晶钻白", "存储": "512GB", "网络": "WiFi"}', 'https://img.example.com/sku/matepadpro132-white.png'),

-- AirPods Pro 2
(33, 18, 'APP2-WT', 1899.00, 500, '{"颜色": "白色"}', 'https://img.example.com/sku/airpodspro2-white.png'),

-- AirPods Max
(34, 19, 'APMAX-GY', 4399.00, 80, '{"颜色": "深空灰"}', 'https://img.example.com/sku/airpodsmax-gray.png'),
(35, 19, 'APMAX-SL', 4399.00, 80, '{"颜色": "银色"}', 'https://img.example.com/sku/airpodsmax-silver.png'),

-- Sony WH-1000XM6
(36, 20, 'WH1000XM6-BK', 2899.00, 120, '{"颜色": "黑色"}', 'https://img.example.com/sku/wh1000xm6-black.png'),
(37, 20, 'WH1000XM6-SL', 2899.00, 100, '{"颜色": "银色"}', 'https://img.example.com/sku/wh1000xm6-silver.png'),

-- Bose QuietComfort Ultra
(38, 21, 'BOSEQCU-BK', 2599.00, 100, '{"颜色": "黑色"}', 'https://img.example.com/sku/boseqcu-black.png'),
(39, 21, 'BOSEQCU-WT', 2599.00, 80, '{"颜色": "白色"}', 'https://img.example.com/sku/boseqcu-white.png'),

-- Samsung Galaxy Buds3 Pro
(40, 22, 'SGB3PRO-SL', 1599.00, 200, '{"颜色": "星际银"}', 'https://img.example.com/sku/buds3pro-silver.png'),

-- Sony WF-1000XM6
(41, 23, 'WF1000XM6-BK', 1999.00, 150, '{"颜色": "黑色"}', 'https://img.example.com/sku/wf1000xm6-black.png'),
(42, 23, 'WF1000XM6-PL', 1999.00, 120, '{"颜色": "铂金银"}', 'https://img.example.com/sku/wf1000xm6-platinum.png'),

-- Apple Watch Ultra 3
(43, 24, 'AWU3-49-GPS-CELL-TI', 6499.00, 60, '{"颜色": "钛金属原色", "尺寸": "49mm", "网络": "GPS+蜂窝", "表带": "高山回环式"}', 'https://img.example.com/sku/watchultra3-titanium.png'),

-- Apple Watch Series 10
(44, 25, 'AWS10-46-GPS-AL-MN', 2999.00, 200, '{"颜色": "午夜色铝金属", "尺寸": "46mm", "网络": "GPS"}', 'https://img.example.com/sku/watchs10-midnight-al.png'),
(45, 25, 'AWS10-46-CELL-AL-SL', 3799.00, 150, '{"颜色": "星光色铝金属", "尺寸": "46mm", "网络": "GPS+蜂窝"}', 'https://img.example.com/sku/watchs10-starlight-cell.png'),

-- Samsung Galaxy Watch7 Ultra
(46, 26, 'SGW7U-47-LTE-GY', 3999.00, 80, '{"颜色": "钛岩灰", "尺寸": "47mm", "网络": "LTE"}', 'https://img.example.com/sku/watch7ultra-gray.png'),

-- Huawei Watch GT 5 Pro
(47, 27, 'HWGT5P-46-FLUO-BK', 2488.00, 120, '{"颜色": "曜石黑", "尺寸": "46mm", "表带": "氟橡胶"}', 'https://img.example.com/sku/watchgt5pro-46-black.png'),
(48, 27, 'HWGT5P-42-CER-WT', 2788.00, 80, '{"颜色": "冰川白", "尺寸": "42mm", "表带": "陶瓷"}', 'https://img.example.com/sku/watchgt5pro-42-white.png'),

-- Garmin Fenix 8
(49, 28, 'FENIX8-47-AMOLED-TI', 7980.00, 50, '{"颜色": "碳灰色钛合金", "尺寸": "47mm", "屏幕": "AMOLED"}', 'https://img.example.com/sku/fenix8-47-amoled.png'),
(50, 28, 'FENIX8-51-SOLAR-GY', 8480.00, 40, '{"颜色": "精英灰", "尺寸": "51mm", "屏幕": "太阳能充电 MIP"}', 'https://img.example.com/sku/fenix8-51-solar.png'),

-- Nintendo Switch OLED
(51, 29, 'NSOLED-WT', 2599.00, 300, '{"颜色": "白色 Joy-Con"}', 'https://img.example.com/sku/switcholed-white.png'),
(52, 29, 'NSOLED-RB', 2599.00, 350, '{"颜色": "马力欧红蓝 Joy-Con"}', 'https://img.example.com/sku/switcholed-redblue.png'),

-- PlayStation 5 Pro
(53, 30, 'PS5PRO-STD', 5799.00, 200, '{"版本": "标准版"}', 'https://img.example.com/sku/ps5pro-standard.png'),

-- Xbox Series X (2024)
(54, 31, 'XBSX24-STD-BK', 3899.00, 180, '{"颜色": "碳黑", "版本": "数字版 2TB"}', 'https://img.example.com/sku/xboxseriesx-black.png'),

-- Steam Deck OLED
(55, 32, 'SDOLED-512', 4399.00, 100, '{"存储": "512GB", "屏幕": "OLED"}', 'https://img.example.com/sku/steamdeckoled-512.png'),
(56, 32, 'SDOLED-1TB', 4899.00, 60, '{"存储": "1TB", "屏幕": "OLED"}', 'https://img.example.com/sku/steamdeckoled-1tb.png')

ON CONFLICT (id) DO NOTHING;

-- 重置序列值，避免后续 INSERTS 出现主键冲突
SELECT setval('sku_id_seq', (SELECT COALESCE(MAX(id), 0) FROM sku));
SELECT setval('product_id_seq', (SELECT COALESCE(MAX(id), 0) FROM product));
SELECT setval('category_id_seq', (SELECT COALESCE(MAX(id), 0) FROM category));

COMMIT;
