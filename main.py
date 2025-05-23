import mysql.connector
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from collections import Counter, defaultdict
import json
from fastapi.middleware.cors import CORSMiddleware
import random
import numpy as np
from typing import List, Optional

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

# 預測參數模型
class PredictionParams(BaseModel):
    periods: int = 10
    hot_weight: float = 0.7
    cold_weight: float = 0.3
    num_combinations: int = 5

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
        "latest_draw": formatted_draws[0] if formatted_draws else []
    }

# 取得指定期數的歷史開獎記錄
@app.get("/history/{periods}")
async def get_history(periods: int = 10):
    if periods <= 0:
        raise HTTPException(status_code=400, detail="期數必須大於 0")
        
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    cursor.execute(f"SELECT * FROM bingo_draws ORDER BY draw_date DESC LIMIT {periods}")
    draws = cursor.fetchall()
    
    formatted_draws = []
    for draw in draws:
        num_list = [draw[f'num{i}'] for i in range(1, 11)]
        formatted_draws.append({
            "draw_date": draw["draw_date"].isoformat() if draw["draw_date"] else None,
            "numbers": num_list
        })
    
    cursor.close()
    conn.close()
    
    return {"draws": formatted_draws}

# 預測下一期號碼
@app.post("/predict")
async def predict_numbers(params: PredictionParams):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    cursor.execute(f"SELECT * FROM bingo_draws ORDER BY draw_date DESC LIMIT {params.periods}")
    draws = cursor.fetchall()
    
    if len(draws) < 5:
        raise HTTPException(status_code=400, detail="至少需要 5 期資料才能預測")
    
    all_numbers = []
    for draw in draws:
        num_list = [draw[f'num{i}'] for i in range(1, 11)]
        all_numbers.extend(num_list)
    
    # 計算每個號碼出現次數
    number_counts = Counter(all_numbers)
    total_numbers = len(draws) * 10
    
    # 計算每個號碼的出現機率
    probabilities = {}
    for num in range(1, 81):
        # 基礎機率
        base_prob = number_counts.get(num, 0) / total_numbers
        
        # 熱號加權 (出現頻率高的號碼)
        if num in [n for n, _ in number_counts.most_common(15)]:
            probabilities[num] = base_prob * params.hot_weight
        # 冷號加權 (出現頻率低或未出現的號碼)
        elif num not in number_counts or num in [n for n, _ in number_counts.most_common()[:-16:-1]]:
            # 如果完全沒出現過，給予一個小的基礎機率
            if num not in number_counts:
                probabilities[num] = 0.01 * params.cold_weight
            else:
                probabilities[num] = (1 - base_prob) * params.cold_weight
        else:
            probabilities[num] = base_prob
    
    # 正規化機率，確保總和為 1
    total_prob = sum(probabilities.values())
    for num in probabilities:
        probabilities[num] /= total_prob
    
    # 收集統計信息
    hot_numbers = [num for num, _ in number_counts.most_common(10)]
    cold_numbers = [num for num in range(1, 81) if num not in number_counts]
    if not cold_numbers:
        cold_numbers = [num for num, _ in number_counts.most_common()[:-11:-1]]
    
    # 按機率生成多組推薦號碼
    recommendations = []
    all_nums = list(range(1, 81))
    
    for _ in range(params.num_combinations):
        # 使用加權機率隨機選擇 10 個號碼
        prediction = np.random.choice(
            all_nums, 
            size=10, 
            replace=False, 
            p=[probabilities[i] for i in all_nums]
        ).tolist()
        recommendations.append(sorted(prediction))
    
    # 計算每個號碼的推薦指數（基於其機率）
    recommendation_scores = {}
    for num in range(1, 81):
        score = probabilities[num] * 100  # 轉換為百分比
        recommendation_scores[num] = round(score, 2)
    
    # 取得機率前 20 名的號碼
    top_numbers = sorted(recommendation_scores.items(), key=lambda x: x[1], reverse=True)[:20]
    
    cursor.close()
    conn.close()
    
    # 熱號/冷號出現機率可視化數據
    visualization_data = []
    for num in range(1, 81):
        visualization_data.append({
            "number": num,
            "frequency": number_counts.get(num, 0),
            "probability": round(probabilities[num] * 100, 2)  # 百分比形式
        })
    
    return {
        "hot_numbers": hot_numbers,
        "cold_numbers": cold_numbers,
        "number_frequencies": dict(number_counts),
        "recommended_combinations": recommendations,
        "number_probabilities": recommendation_scores,
        "top_numbers": top_numbers,
        "visualization_data": visualization_data
    }
