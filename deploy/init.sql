-- English Mastery 数据库初始化脚本

-- 设置字符集
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS english_mastery
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE english_mastery;

-- ==================== 用户表 ====================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    avatar VARCHAR(500),
    wechat_openid VARCHAR(100) UNIQUE,
    wechat_unionid VARCHAR(100),
    google_id VARCHAR(100) UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login_at DATETIME,
    INDEX idx_email (email),
    INDEX idx_phone (phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==================== 会员表 ====================
CREATE TABLE IF NOT EXISTS memberships (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    level ENUM('free', 'basic', 'premium') DEFAULT 'free',
    start_date DATETIME,
    end_date DATETIME,
    auto_renew BOOLEAN DEFAULT FALSE,
    renew_product_id VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==================== 学习进度表 ====================
CREATE TABLE IF NOT EXISTS learning_progress (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    vocabulary FLOAT DEFAULT 0,
    listening FLOAT DEFAULT 0,
    reading FLOAT DEFAULT 0,
    writing FLOAT DEFAULT 0,
    speaking FLOAT DEFAULT 0,
    overall FLOAT DEFAULT 0,
    current_day INT DEFAULT 1,
    start_date DATE DEFAULT (CURRENT_DATE),
    total_study_time INT DEFAULT 0 COMMENT '总学习时长(分钟)',
    words_learned INT DEFAULT 0,
    streak_days INT DEFAULT 0 COMMENT '连续打卡天数',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==================== 打卡记录表 ====================
CREATE TABLE IF NOT EXISTS checkin_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    checkin_date DATE NOT NULL,
    tasks JSON DEFAULT '[]' COMMENT '完成的任务列表',
    study_time INT DEFAULT 0 COMMENT '学习时长(分钟)',
    note TEXT COMMENT '学习备注',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY uk_user_date (user_id, checkin_date),
    INDEX idx_user_id (user_id),
    INDEX idx_checkin_date (checkin_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==================== 订单表 ====================
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_no VARCHAR(64) UNIQUE NOT NULL,
    user_id INT NOT NULL,
    product_type ENUM('basic_monthly', 'basic_yearly', 'premium_monthly', 'premium_yearly', 'course') NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    product_id VARCHAR(50),
    amount DECIMAL(10, 2) NOT NULL,
    actual_amount DECIMAL(10, 2) NOT NULL,
    discount_amount DECIMAL(10, 2) DEFAULT 0,
    pay_method ENUM('wechat', 'alipay'),
    status ENUM('pending', 'paid', 'cancelled', 'refunded', 'failed') DEFAULT 'pending',
    trade_no VARCHAR(64) COMMENT '第三方交易号',
    pay_time DATETIME,
    refund_no VARCHAR(64),
    refund_amount DECIMAL(10, 2),
    refund_time DATETIME,
    refund_reason TEXT,
    remark TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    expire_at DATETIME COMMENT '订单过期时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_order_no (order_no),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==================== 词汇表 ====================
CREATE TABLE IF NOT EXISTS vocabularies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    word VARCHAR(100) NOT NULL,
    phonetic VARCHAR(100),
    pronunciation_url VARCHAR(500),
    translation VARCHAR(500) NOT NULL,
    definition TEXT,
    example TEXT,
    example_translation TEXT,
    day INT NOT NULL COMMENT '所属天数(1-30)',
    category VARCHAR(50) COMMENT '分类(商务/学术等)',
    level ENUM('beginner', 'intermediate', 'advanced') DEFAULT 'intermediate',
    synonyms JSON DEFAULT '[]',
    antonyms JSON DEFAULT '[]',
    collocations JSON DEFAULT '[]' COMMENT '常见搭配',
    is_active BOOLEAN DEFAULT TRUE,
    is_premium BOOLEAN DEFAULT FALSE COMMENT '是否会员专属',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_word (word),
    INDEX idx_day (day)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==================== 课程表 ====================
CREATE TABLE IF NOT EXISTS courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    cover_url VARCHAR(500),
    type VARCHAR(50) NOT NULL COMMENT '类型(listening/reading/writing)',
    level ENUM('beginner', 'intermediate', 'advanced') DEFAULT 'intermediate',
    day INT COMMENT '所属天数',
    content JSON DEFAULT '{}' COMMENT '课程内容',
    duration INT DEFAULT 0 COMMENT '预计时长(分钟)',
    is_active BOOLEAN DEFAULT TRUE,
    is_premium BOOLEAN DEFAULT FALSE,
    sort_order INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_type (type),
    INDEX idx_day (day)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==================== 学习材料表 ====================
CREATE TABLE IF NOT EXISTS learning_materials (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT,
    title VARCHAR(200) NOT NULL,
    type VARCHAR(50) NOT NULL COMMENT '类型(audio/video/document)',
    url VARCHAR(500) NOT NULL,
    thumbnail_url VARCHAR(500),
    duration INT DEFAULT 0 COMMENT '时长(秒)',
    size INT DEFAULT 0 COMMENT '文件大小(字节)',
    transcript TEXT COMMENT '文字稿/字幕',
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_premium BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE SET NULL,
    INDEX idx_course_id (course_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==================== 插入示例词汇数据 ====================
INSERT INTO vocabularies (word, phonetic, translation, definition, example, example_translation, day, category, level) VALUES
-- Day 1
('acquisition', '/ˌækwɪˈzɪʃn/', '收购；获得', 'The process of buying a company or obtaining something', 'The acquisition of the startup was completed last week.', '这家初创公司的收购已于上周完成。', 1, '商务', 'advanced'),
('benchmark', '/ˈbentʃmɑːrk/', '基准；标杆', 'A standard against which things are compared', 'We use industry benchmarks to measure our performance.', '我们使用行业基准来衡量我们的业绩。', 1, '商务', 'intermediate'),
('compliance', '/kəmˈplaɪəns/', '合规；遵从', 'The act of obeying rules or requests', 'Ensuring compliance with data protection regulations is essential.', '确保遵守数据保护法规至关重要。', 1, '法律', 'advanced'),
('delegate', '/ˈdelɪɡeɪt/', '委派；代表', 'To give a task or responsibility to someone else', 'You need to learn to delegate tasks to your team.', '你需要学会将任务委派给你的团队。', 1, '管理', 'intermediate'),
('execute', '/ˈeksɪkjuːt/', '执行；实施', 'To carry out or put into effect', 'The team executed the marketing plan flawlessly.', '团队完美地执行了营销计划。', 1, '商务', 'intermediate'),
-- Day 2
('feasibility', '/ˌfiːzəˈbɪləti/', '可行性', 'The possibility of being done', 'We conducted a feasibility study before starting the project.', '在启动项目之前，我们进行了可行性研究。', 2, '项目管理', 'advanced'),
('leverage', '/ˈlevərɪdʒ/', '利用；杠杆', 'To use something to maximum advantage', 'We need to leverage our existing customer base.', '我们需要充分利用现有的客户群。', 2, '商务', 'intermediate'),
('milestone', '/ˈmaɪlstəʊn/', '里程碑', 'An important event or stage in development', 'Reaching 1 million users was a major milestone for us.', '达到100万用户对我们来说是一个重要的里程碑。', 2, '项目管理', 'intermediate'),
('negotiate', '/nɪˈɡəʊʃieɪt/', '谈判；协商', 'To discuss in order to reach an agreement', 'We successfully negotiated a better contract.', '我们成功谈判达成了一份更好的合同。', 2, '商务', 'intermediate'),
('optimize', '/ˈɒptɪmaɪz/', '优化', 'To make as effective as possible', 'We need to optimize our workflow for better efficiency.', '我们需要优化工作流程以提高效率。', 2, '技术', 'intermediate');

-- 提示完成
SELECT 'Database initialization completed!' AS Status;
