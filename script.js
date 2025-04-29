let selectedNumbers = [];
let frequencyChart = null;
let probabilityChart = null;

// API基礎URL
const API_BASE_URL = "http://localhost:8000";

function createNumberGrid() {
    const grid = document.getElementById("number-grid");
    grid.innerHTML = "";
    for (let i = 1; i <= 80; i++) {
        const btn = document.createElement("button");
        btn.innerText = i;
        btn.classList.add("number-btn");
        btn.onclick = () => toggleNumber(i, btn);
        grid.appendChild(btn);
    }
}

function toggleNumber(num, btn) {
    if (selectedNumbers.includes(num)) {
        selectedNumbers = selectedNumbers.filter(n => n !== num);
        btn.classList.remove("selected");
    } else if (selectedNumbers.length < 10) {
        selectedNumbers.push(num);
        btn.classList.add("selected");
    }
}

async function submitDraw() {
    if (selectedNumbers.length !== 10) {
        alert("請選擇 10 個數字!");
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/new_draw`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ numbers: selectedNumbers })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        alert(data.message);
        selectedNumbers = [];
        createNumberGrid();
    } catch (error) {
        console.error("請求失敗:", error);
        alert("提交失敗，請確認後端是否運行。請確保後端服務在端口8000運行，前端在端口8080運行。");
        checkBackendConnection();  // 再次檢查連接
    }
}

async function fetchStatistics() {
    try {
        const response = await fetch(`${API_BASE_URL}/statistics`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const data = await response.json();

        let statsHtml = `
            <h3>本期號碼: ${formatArray(data.latest_draw)}</h3>
            <h3>熱門號碼: ${formatArray(data.hot_numbers)}</h3>
            <h3>冷門號碼: ${formatArray(data.cold_numbers)}</h3>
            <h3>二連號: ${formatStreaks(data.two_streaks)}</h3>
            <h3>三連號: ${formatStreaks(data.three_streaks)}</h3>
            <h3>四連號: ${formatStreaks(data.four_streaks)}</h3>
            <h3>熱門頭號: ${formatArray(data.hot_heads)}</h3>
            <h3>熱門尾號: ${formatArray(data.hot_tails)}</h3>
        `;

        document.getElementById("statistics").innerHTML = statsHtml;
    } catch (error) {
        console.error("獲取統計數據失敗:", error);
        document.getElementById("statistics").innerHTML = 
            "<p>獲取數據失敗，請確認後端是否運行在端口8000。如果已輸入數據，請確認至少有5期開獎號碼。</p>";
        checkBackendConnection();  // 再次檢查連接
    }
}

function formatArray(arr) {
    if (!arr || arr.length === 0) return "無數據";
    return arr.join(", ");
}

function formatStreaks(streaks) {
    if (!streaks || streaks.length === 0) return "無數據";
    return streaks.map(s => {
        const [numbers, count] = s;
        return `${numbers.join("-")} (${count}次)`;
    }).join(", ");
}

// 監聽熱號冷號權重滑塊
document.addEventListener('DOMContentLoaded', function() {
    const hotWeightInput = document.getElementById('hot-weight');
    const coldWeightInput = document.getElementById('cold-weight');
    
    if (hotWeightInput) {
        hotWeightInput.addEventListener('input', function() {
            document.getElementById('hot-weight-value').textContent = this.value;
        });
    }
    
    if (coldWeightInput) {
        coldWeightInput.addEventListener('input', function() {
            document.getElementById('cold-weight-value').textContent = this.value;
        });
    }
    
    // 初始檢查後端連接
    checkBackendConnection();
});

// 預測號碼
async function predictNumbers() {
    try {
        const periods = document.getElementById('periods').value;
        const hotWeight = document.getElementById('hot-weight').value;
        const coldWeight = document.getElementById('cold-weight').value;
        const combinations = document.getElementById('combinations').value;
        
        const response = await fetch(`${API_BASE_URL}/predict`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                periods: parseInt(periods),
                hot_weight: parseFloat(hotWeight),
                cold_weight: parseFloat(coldWeight),
                num_combinations: parseInt(combinations)
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const data = await response.json();
        displayPredictionResults(data);
    } catch (error) {
        console.error("預測失敗:", error);
        document.getElementById("recommended-numbers").innerHTML = 
            "<p>預測失敗，請確認後端服務是否運行在端口8000，且已輸入至少5期開獎號碼</p>";
        checkBackendConnection();  // 再次檢查連接
    }
}

// 檢查後端連接
async function checkBackendConnection() {
    const statusElement = document.getElementById('connection-status');
    
    try {
        // 使用簡單的GET請求檢查後端是否在線
        const response = await fetch(`${API_BASE_URL}/docs`, { 
            method: 'GET',
            // 設置超時為3秒
            signal: AbortSignal.timeout(3000)
        });
        
        if (response.ok) {
            statusElement.textContent = '後端服務連接成功';
            statusElement.className = 'connection-status connected';
            console.log('後端服務連接成功');
            return true;
        } else {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
    } catch (error) {
        statusElement.textContent = '後端服務連接失敗 - 請確保後端服務在8000端口運行';
        statusElement.className = 'connection-status disconnected';
        console.error('後端服務連接失敗:', error);
        return false;
    }
}

// 顯示預測結果
function displayPredictionResults(data) {
    // 顯示推薦號碼組合
    displayRecommendedNumbers(data);
    
    // 顯示頻率圖表
    createFrequencyChart(data.visualization_data);
    
    // 顯示機率圖表
    createProbabilityChart(data.visualization_data);
}

// 顯示推薦號碼組合
function displayRecommendedNumbers(data) {
    const container = document.getElementById("recommended-numbers");
    container.innerHTML = "<h3>推薦號碼組合</h3>";
    
    // 顯示熱門/冷門號碼
    const hotColdSection = document.createElement("div");
    hotColdSection.innerHTML = `
        <div class="number-stats">
            <h4>熱門號碼：</h4>
            ${data.hot_numbers.map(num => `<div class="number-stat hot">${num}</div>`).join("")}
        </div>
        <div class="number-stats">
            <h4>冷門號碼：</h4>
            ${data.cold_numbers.map(num => `<div class="number-stat cold">${num}</div>`).join("")}
        </div>
    `;
    container.appendChild(hotColdSection);
    
    // 顯示推薦組合
    const combosSection = document.createElement("div");
    combosSection.innerHTML = "<h4>推薦組合：</h4>";
    
    data.recommended_combinations.forEach((combo, index) => {
        const hotNums = data.hot_numbers;
        const coldNums = data.cold_numbers;
        
        const comboDiv = document.createElement("div");
        comboDiv.classList.add("recommended-set");
        comboDiv.innerHTML = `<div>組合 ${index + 1}：</div>`;
        
        // 為每個號碼創建元素，添加熱號/冷號標記
        combo.forEach(num => {
            const numSpan = document.createElement("span");
            numSpan.classList.add("recommended-number");
            if (hotNums.includes(num)) {
                numSpan.classList.add("hot");
            } else if (coldNums.includes(num)) {
                numSpan.classList.add("cold");
            }
            numSpan.textContent = num;
            comboDiv.appendChild(numSpan);
        });
        
        combosSection.appendChild(comboDiv);
    });
    
    container.appendChild(combosSection);
    
    // 顯示機率最高的前20個號碼
    const topSection = document.createElement("div");
    topSection.innerHTML = "<h4>機率最高的號碼：</h4>";
    
    const topStatsDiv = document.createElement("div");
    topStatsDiv.classList.add("number-stats");
    
    data.top_numbers.forEach(([num, probability]) => {
        const numDiv = document.createElement("div");
        numDiv.classList.add("number-stat");
        if (data.hot_numbers.includes(num)) {
            numDiv.classList.add("hot");
        } else if (data.cold_numbers.includes(num)) {
            numDiv.classList.add("cold");
        }
        
        numDiv.innerHTML = `
            ${num}
            <span class="tooltip">機率: ${probability}%</span>
        `;
        
        topStatsDiv.appendChild(numDiv);
    });
    
    topSection.appendChild(topStatsDiv);
    container.appendChild(topSection);
}

// 創建頻率圖表
function createFrequencyChart(data) {
    const ctx = document.getElementById('frequencyChart').getContext('2d');
    
    // 若已存在圖表則銷毀
    if (frequencyChart) {
        frequencyChart.destroy();
    }
    
    // 按頻率排序，取前20個
    const sortedData = [...data].sort((a, b) => b.frequency - a.frequency).slice(0, 20);
    
    frequencyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sortedData.map(item => item.number),
            datasets: [{
                label: '出現頻率',
                data: sortedData.map(item => item.frequency),
                backgroundColor: sortedData.map(item => 
                    item.type === 'hot' ? 'rgba(255, 99, 132, 0.6)' : 
                    item.type === 'cold' ? 'rgba(54, 162, 235, 0.6)' : 
                    'rgba(153, 102, 255, 0.6)'
                ),
                borderColor: sortedData.map(item => 
                    item.type === 'hot' ? 'rgba(255, 99, 132, 1)' : 
                    item.type === 'cold' ? 'rgba(54, 162, 235, 1)' : 
                    'rgba(153, 102, 255, 1)'
                ),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: '出現次數'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: '號碼'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: '號碼出現頻率（前20名）'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const item = sortedData[context.dataIndex];
                            let label = `出現次數: ${item.frequency}`;
                            if (item.type === 'hot') {
                                label += ' (熱號)';
                            } else if (item.type === 'cold') {
                                label += ' (冷號)';
                            }
                            return label;
                        }
                    }
                }
            }
        }
    });
}

// 創建機率圖表
function createProbabilityChart(data) {
    const ctx = document.getElementById('probabilityChart').getContext('2d');
    
    // 若已存在圖表則銷毀
    if (probabilityChart) {
        probabilityChart.destroy();
    }
    
    // 按機率排序，取前20個
    const sortedData = [...data].sort((a, b) => b.probability - a.probability).slice(0, 20);
    
    probabilityChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sortedData.map(item => item.number),
            datasets: [{
                label: '預測機率',
                data: sortedData.map(item => item.probability),
                backgroundColor: sortedData.map(item => 
                    item.type === 'hot' ? 'rgba(255, 99, 132, 0.6)' : 
                    item.type === 'cold' ? 'rgba(75, 192, 192, 0.6)' : 
                    'rgba(153, 102, 255, 0.6)'
                ),
                borderColor: sortedData.map(item => 
                    item.type === 'hot' ? 'rgba(255, 99, 132, 1)' : 
                    item.type === 'cold' ? 'rgba(75, 192, 192, 1)' : 
                    'rgba(153, 102, 255, 1)'
                ),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: '機率 (%)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: '號碼'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: '號碼預測機率（前20名）'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const item = sortedData[context.dataIndex];
                            let label = `預測機率: ${item.probability}%`;
                            if (item.type === 'hot') {
                                label += ' (熱門號碼)';
                            } else if (item.type === 'cold') {
                                label += ' (冷門號碼)';
                            }
                            return label;
                        }
                    }
                }
            }
        }
    });
}

// 定期檢查後端連接狀態
setInterval(checkBackendConnection, 30000); // 每30秒檢查一次

createNumberGrid();
