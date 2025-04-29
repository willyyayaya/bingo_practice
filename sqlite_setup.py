import sqlite3
import json

# 連接到SQLite數據庫
conn = sqlite3.connect('bingo.db')
cursor = conn.cursor()

# 創建開獎記錄表
cursor.execute('''
CREATE TABLE IF NOT EXISTS bingo_draws (
    draw_id INTEGER PRIMARY KEY AUTOINCREMENT,
    draw_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    num1 INTEGER NOT NULL,
    num2 INTEGER NOT NULL,
    num3 INTEGER NOT NULL,
    num4 INTEGER NOT NULL,
    num5 INTEGER NOT NULL,
    num6 INTEGER NOT NULL,
    num7 INTEGER NOT NULL,
    num8 INTEGER NOT NULL,
    num9 INTEGER NOT NULL,
    num10 INTEGER NOT NULL
)
''')

# 創建統計數據表
cursor.execute('''
CREATE TABLE IF NOT EXISTS bingo_statistics (
    stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    hot_numbers TEXT,
    cold_numbers TEXT,
    two_streaks TEXT,
    three_streaks TEXT,
    four_streaks TEXT,
    hot_heads TEXT,
    hot_tails TEXT,
    two_same TEXT,
    three_same TEXT
)
''')

# 插入測試數據
test_data = [
    (5, 12, 24, 36, 42, 48, 53, 65, 71, 79),
    (3, 14, 22, 31, 45, 52, 57, 62, 70, 78),
    (8, 16, 23, 37, 44, 51, 59, 63, 72, 75),
    (2, 11, 25, 35, 43, 49, 58, 64, 73, 77),
    (7, 15, 21, 33, 41, 50, 56, 66, 74, 80)
]

cursor.executemany('''
INSERT INTO bingo_draws (num1, num2, num3, num4, num5, num6, num7, num8, num9, num10)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', test_data)

# 提交更改並關閉連接
conn.commit()
conn.close()

print("SQLite數據庫已創建成功，並插入了測試數據。") 