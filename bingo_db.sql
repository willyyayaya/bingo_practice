-- 創建數據庫
CREATE DATABASE IF NOT EXISTS bingo_db;

-- 使用數據庫
USE bingo_db;

-- 創建開獎記錄表
CREATE TABLE IF NOT EXISTS bingo_draws (
    draw_id INT AUTO_INCREMENT PRIMARY KEY,
    draw_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    num1 INT NOT NULL,
    num2 INT NOT NULL,
    num3 INT NOT NULL,
    num4 INT NOT NULL,
    num5 INT NOT NULL,
    num6 INT NOT NULL,
    num7 INT NOT NULL,
    num8 INT NOT NULL,
    num9 INT NOT NULL,
    num10 INT NOT NULL
);

-- 創建統計數據表
CREATE TABLE IF NOT EXISTS bingo_statistics (
    stat_id INT AUTO_INCREMENT PRIMARY KEY,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    hot_numbers JSON,
    cold_numbers JSON,
    two_streaks JSON,
    three_streaks JSON,
    four_streaks JSON,
    hot_heads JSON,
    hot_tails JSON,
    two_same JSON,
    three_same JSON
);

-- 插入一些測試數據（如果需要）
INSERT INTO bingo_draws (num1, num2, num3, num4, num5, num6, num7, num8, num9, num10)
VALUES
    (5, 12, 24, 36, 42, 48, 53, 65, 71, 79),
    (3, 14, 22, 31, 45, 52, 57, 62, 70, 78),
    (8, 16, 23, 37, 44, 51, 59, 63, 72, 75),
    (2, 11, 25, 35, 43, 49, 58, 64, 73, 77),
    (7, 15, 21, 33, 41, 50, 56, 66, 74, 80); 