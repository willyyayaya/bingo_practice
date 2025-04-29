import sqlite3
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

# 數字輸入模型
class NumberSelection(BaseModel):
    numbers: list[int]

# 預測參數模型
class PredictionParams(BaseModel):
    periods: int = 10
    hot_weight: float = 0.7
    cold_weight: float = 0.3
    num_combinations: int = 5

# SQLite連接函數
def get_db_connection():
    conn = sqlite3.connect('bingo.db')
    conn.row_factory = sqlite3.Row
    return conn

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

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO bingo_draws (num1, num2, num3, num4, num5, num6, num7, num8, num9, num10)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cursor.execute(query, tuple(request.numbers))

    conn.commit()
    cursor.close()
    conn.close()

    return {"message": "開獎號碼已記錄"}

# 查詢近五期並統計熱門冷門號碼
@app.get("/statistics")
async def get_statistics():
    conn = get_db_connection()
    cursor = conn.cursor()

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

    # 將JSON數據轉為字符串
    stats_data = {
        "hot_numbers": json.dumps(hot_numbers),
        "cold_numbers": json.dumps(cold_numbers),
        "two_streaks": json.dumps(two_streaks),
        "three_streaks": json.dumps(three_streaks),
        "four_streaks": json.dumps(four_streaks),
        "hot_heads": json.dumps(hot_heads),
        "hot_tails": json.dumps(hot_tails),
        "two_same": json.dumps(two_same),
        "three_same": json.dumps(three_same)
    }
    
    cursor.execute("""
    INSERT INTO bingo_statistics 
    (hot_numbers, cold_numbers, two_streaks, three_streaks, four_streaks, 
    hot_heads, hot_tails, two_same, three_same)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        stats_data["hot_numbers"],
        stats_data["cold_numbers"],
        stats_data["two_streaks"],
        stats_data["three_streaks"],
        stats_data["four_streaks"],
        stats_data["hot_heads"],
        stats_data["hot_tails"],
        stats_data["two_same"],
        stats_data["three_same"]
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
        
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM bingo_draws ORDER BY draw_date DESC LIMIT {periods}")
    draws = cursor.fetchall()
    
    formatted_draws = []
    for draw in draws:
        num_list = [draw[f'num{i}'] for i in range(1, 11)]
        draw_date = draw["draw_date"] if "draw_date" in draw.keys() else None
        formatted_draws.append({
            "draw_date": draw_date,
            "numbers": num_list
        })
    
    cursor.close()
    conn.close()
    
    return {"draws": formatted_draws}

# 預測下一期號碼
@app.post("/predict")
async def predict_numbers(params: PredictionParams):
    conn = get_db_connection()
    cursor = conn.cursor()

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
    
    # 定義熱號和冷號的閾值
    hot_threshold = 0.015  # 出現頻率高於1.5%視為熱號
    cold_threshold = 0.005  # 出現頻率低於0.5%視為冷號
    
    # 按次數排序所有號碼
    sorted_numbers = sorted([(n, count) for n, count in number_counts.items()], 
                            key=lambda x: x[1], reverse=True)
    
    # 計算每個號碼的出現機率
    probabilities = {}
    for num in range(1, 81):
        # 基礎機率 - 每個號碼在數據集中的實際出現頻率
        base_prob = number_counts.get(num, 0) / total_numbers
        
        # 分類號碼
        if base_prob >= hot_threshold:
            # 熱號 - 加強其機率
            probabilities[num] = base_prob * params.hot_weight
        elif base_prob <= cold_threshold or num not in number_counts:
            # 冷號或從未出現的號碼
            if num not in number_counts:
                # 從未出現的號碼給予一個基礎機率
                base_prob = 1 / (total_numbers * 2)  # 較小但非零的機率
            # 冷號使用反向加權，越冷機率反而越高（假設冷號可能即將出現）
            cold_factor = cold_threshold / (base_prob + 0.0001)  # 避免除以零
            probabilities[num] = base_prob * cold_factor * params.cold_weight
        else:
            # 中性號碼 - 保持原有機率
            probabilities[num] = base_prob
    
    # 正規化機率，確保總和為 1
    total_prob = sum(probabilities.values())
    for num in probabilities:
        probabilities[num] /= total_prob
    
    # 收集統計信息
    # 熱號 - 前10個高頻號碼
    hot_numbers = [n for n, _ in sorted_numbers[:10]] if sorted_numbers else []
    # 冷號 - 所有未出現或出現次數最少的號碼（至多10個）
    never_appeared = [n for n in range(1, 81) if n not in number_counts]
    rare_numbers = [n for n, _ in sorted_numbers[-10:]] if sorted_numbers else []
    cold_numbers = never_appeared + rare_numbers
    cold_numbers = cold_numbers[:10]  # 最多取10個冷號
    
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
            "probability": round(probabilities[num] * 100, 2),  # 百分比形式
            "type": "hot" if num in hot_numbers else ("cold" if num in cold_numbers else "neutral")
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