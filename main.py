import mysql.connector
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from collections import Counter, defaultdict
import json
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS 設定，讓前端可以存取 API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MySQL 連線設定
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "bingo_db",
}

# 數字輸入模型
class NumberSelection(BaseModel):
    numbers: list[int]

# 計算連號
def find_streaks(numbers_list, streak_length):
    streaks = defaultdict(int)
    for draw in numbers_list:
        sorted_draw = sorted(draw)
        for i in range(len(sorted_draw) - (streak_length - 1)):
            streak = tuple(sorted_draw[i:i + streak_length])
            streaks[streak] += 1
    return sorted(streaks.items(), key=lambda x: x[1], reverse=True)[:5]

# 新增開獎號碼
@app.post("/new_draw")
async def add_new_draw(request: NumberSelection):
    if len(request.numbers) != 10:
        raise HTTPException(status_code=400, detail="請選擇 10 個數字")

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    query = """
    INSERT INTO bingo_draws (num1, num2, num3, num4, num5, num6, num7, num8, num9, num10)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, tuple(request.numbers))

    conn.commit()
    cursor.close()
    conn.close()

    return {"message": "開獎號碼已記錄"}

# 查詢近五期並統計熱門冷門號碼
@app.get("/statistics")
async def get_statistics():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM bingo_draws ORDER BY draw_date DESC LIMIT 5")
    last_5_draws = cursor.fetchall()
    
    if len(last_5_draws) < 5:
        raise HTTPException(status_code=400, detail="至少需輸入 5 期開獎號碼才能分析")

    all_numbers = []
    formatted_draws = []
    for draw in last_5_draws:
        num_list = [draw[f'num{i}'] for i in range(1, 11)]
        all_numbers.extend(num_list)
        formatted_draws.append(num_list)

    counter = Counter(all_numbers)

    hot_numbers = [num for num, _ in counter.most_common(5)]
    cold_numbers = [num for num, _ in counter.most_common()[:-6:-1]]

    two_streaks = find_streaks(formatted_draws, 2)
    three_streaks = find_streaks(formatted_draws, 3)
    four_streaks = find_streaks(formatted_draws, 4)

    first_digits = [num // 10 for num in all_numbers if num > 0]
    last_digits = [num % 10 for num in all_numbers]
    hot_heads = [num for num, _ in Counter(first_digits).most_common(3)]
    hot_tails = [num for num, _ in Counter(last_digits).most_common(3)]

    pair_counts = Counter()
    triplet_counts = Counter()
    for draw in formatted_draws:
        sorted_draw = sorted(draw)
        for i in range(len(sorted_draw) - 1):
            pair_counts[tuple(sorted_draw[i:i + 2])] += 1
        for i in range(len(sorted_draw) - 2):
            triplet_counts[tuple(sorted_draw[i:i + 3])] += 1

    two_same = sorted(pair_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    three_same = sorted(triplet_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    query = """
    INSERT INTO bingo_statistics (
        hot_numbers, cold_numbers, two_streaks, three_streaks, four_streaks, 
        hot_heads, hot_tails, two_same, three_same
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (
        json.dumps(hot_numbers),
        json.dumps(cold_numbers),
        json.dumps(two_streaks),
        json.dumps(three_streaks),
        json.dumps(four_streaks),
        json.dumps(hot_heads),
        json.dumps(hot_tails),
        json.dumps(two_same),
        json.dumps(three_same)
    ))

    conn.commit()
    cursor.close()
    conn.close()

    return {
        "hot_numbers": hot_numbers,
        "cold_numbers": cold_numbers,
        "two_streaks": two_streaks,
        "three_streaks": three_streaks,
        "four_streaks": four_streaks,
        "hot_heads": hot_heads,
        "hot_tails": hot_tails,
        "two_same": two_same,
        "three_same": three_same,
        "latest_draw": last_5_draws[-1] if last_5_draws else []
    }
