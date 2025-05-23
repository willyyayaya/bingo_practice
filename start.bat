@echo off
echo 正在設置賓果號碼預測系統...

echo 1. 檢查依賴項...
pip install fastapi uvicorn numpy

echo 2. 設置SQLite數據庫...
python sqlite_setup.py

echo 3. 啟動後端服務（端口8000）...
start cmd /k "uvicorn main_sqlite:app --reload --host 127.0.0.1 --port 8000"

echo 4. 等待後端啟動...
timeout /t 3

echo 5. 啟動前端服務（端口8080）...
start cmd /k "python -m http.server 8080"

echo 系統已啟動!
echo 請在瀏覽器中訪問 http://localhost:8080 查看應用。
echo 按任意鍵退出此窗口...
pause > nul 