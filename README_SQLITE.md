# 賓果號碼預測系統 (SQLite版本)

這是一個基於歷史開獎數據分析和預測賓果號碼的系統，使用FastAPI和SQLite。此版本不需要安裝MySQL，適合快速試用。

## 功能特點

- 輸入歷史開獎號碼
- 統計熱號（高頻率出現的號碼）和冷號（低頻率出現的號碼）
- 分析連號和重複組合模式
- 預測下一期可能的號碼組合
- 視覺化顯示號碼出現頻率和預測機率

## 系統需求

- Python 3.7+
- 現代網頁瀏覽器

## 快速開始

### Windows用戶

1. 雙擊運行 `start.bat` 自動設置和啟動應用

### 手動啟動

1. 安裝依賴:
   ```
   pip install fastapi uvicorn numpy
   ```

2. 設置SQLite數據庫:
   ```
   python sqlite_setup.py
   ```

3. 啟動後端服務:
   ```
   start cmd /k "uvicorn main_sqlite:app --reload --host 127.0.0.1 --port 8000"
   ```

4. 啟動前端服務:
   ```
   start cmd /k "python -m http.server 8080"
   ```

5. 打開瀏覽器訪問 http://localhost:8000

## 如何使用

1. **輸入開獎號碼**: 在網格中選擇10個號碼，然後點擊"提交開獎號碼"
2. **查看統計數據**: 點擊"計算統計數據"顯示熱號、冷號等統計結果
3. **預測號碼**: 設置分析期數、熱/冷號權重後，點擊"預測下一期號碼"

## 數據庫結構

SQLite版本使用以下表結構:

### bingo_draws表
- `draw_id`: 自增主鍵
- `draw_date`: 開獎日期時間戳
- `num1` 到 `num10`: 10個開獎號碼

### bingo_statistics表
- `stat_id`: 自增主鍵
- `create_date`: 創建日期時間戳
- 其餘欄位存儲JSON格式的統計數據

## 文件說明

- `sqlite_setup.py`: 創建SQLite數據庫和表結構
- `main_sqlite.py`: 後端API實現（FastAPI）
- `index.html`: 前端頁面
- `style.css`: 樣式表
- `script.js`: 前端JavaScript代碼
- `start.bat`: Windows快速啟動腳本

## 常見問題

1. **端口被占用**
   - 如果8000端口被占用，可以修改命令為 `python -m http.server 8080` 和 `uvicorn main_sqlite:app --reload --port 8081`

2. **預測功能不工作**
   - 確保已輸入至少5期開獎號碼
   - 檢查開獎號碼是否有效（1-80範圍內）

3. **SQLite數據庫問題**
   - 如果遇到數據庫問題，可以刪除 `bingo.db` 文件並重新運行 `python sqlite_setup.py` 重置數據庫 