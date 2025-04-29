# 賓果號碼預測系統

這是一個基於歷史開獎數據分析和預測賓果號碼的系統，使用FastAPI和MySQL。

## 功能特點

- 輸入歷史開獎號碼
- 統計熱號（高頻率出現的號碼）和冷號（低頻率出現的號碼）
- 分析連號和重複組合模式
- 預測下一期可能的號碼組合
- 視覺化顯示號碼出現頻率和預測機率

## 系統需求

- Python 3.7+
- MySQL 5.7+
- 現代網頁瀏覽器

## 安裝與設置

### 1. 安裝MySQL

#### Windows:
1. 從 [MySQL官網](https://dev.mysql.com/downloads/installer/) 下載MySQL安裝包
2. 運行安裝程序，選擇"Developer Default"選項
3. 設置root密碼（記得修改main.py中的資料庫配置）
4. 完成安裝

#### MacOS:
```
brew install mysql
brew services start mysql
```

#### Linux (Ubuntu):
```
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
```

### 2. 創建數據庫和表

1. 登入MySQL:
```
mysql -u root -p
```

2. 運行SQL腳本創建數據庫和表:
```
mysql -u root -p < bingo_db.sql
```

或者手動複製bingo_db.sql中的內容到MySQL命令行執行。

### 3. 安裝Python依賴

```
pip install fastapi uvicorn mysql-connector-python numpy
```

## 運行應用

1. 啟動後端服務:
```
uvicorn main:app --reload
```

2. 在瀏覽器中訪問 http://localhost:8000/docs 可以查看API文檔

3. 直接在瀏覽器中打開 index.html 使用前端界面

## 如何使用

1. **輸入開獎號碼**: 在網格中選擇10個號碼，然後點擊"提交開獎號碼"
2. **查看統計數據**: 點擊"計算統計數據"顯示熱號、冷號等統計結果
3. **預測號碼**: 設置分析期數、熱/冷號權重後，點擊"預測下一期號碼"

## 數據庫結構

### bingo_draws表
- `draw_id`: 自增主鍵
- `draw_date`: 開獎日期時間戳
- `num1` 到 `num10`: 10個開獎號碼

### bingo_statistics表
- `stat_id`: 自增主鍵
- `create_date`: 創建日期時間戳
- `hot_numbers`: 熱門號碼列表 (JSON)
- `cold_numbers`: 冷門號碼列表 (JSON)
- 其他統計數據欄位 (JSON格式)

## 常見問題

1. **數據庫連接失敗**
   - 檢查MySQL服務是否運行
   - 驗證main.py中的連接參數是否正確

2. **預測功能不工作**
   - 確保已輸入至少5期開獎號碼
   - 檢查開獎號碼是否有效（1-80範圍內）

3. **圖表無法顯示**
   - 確認是否已正確加載Chart.js庫
   - 檢查瀏覽器控制台是否有錯誤消息

---

作者：willyyayaya 
