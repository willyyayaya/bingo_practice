let selectedNumbers = [];

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
        const response = await fetch("http://localhost:8000/new_draw", {
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
        alert("提交失敗，請確認後端是否運行");
    }
}

async function fetchStatistics() {
    const response = await fetch("http://localhost:8000/statistics");
    const data = await response.json();

    let statsHtml = `
        <h3>本期號碼: ${data.latest_draw.num1}, ${data.latest_draw.num2}, ${data.latest_draw.num3}, 
        ${data.latest_draw.num4}, ${data.latest_draw.num5}, ${data.latest_draw.num6}, 
        ${data.latest_draw.num7}, ${data.latest_draw.num8}, ${data.latest_draw.num9}, ${data.latest_draw.num10}</h3>
        <h3>熱門號碼: ${data.hot_numbers.join(", ")}</h3>
        <h3>冷門號碼: ${data.cold_numbers.join(", ")}</h3>
        <h3>二連號: ${data.two_streaks.map(t => t[0].join("-")).join(", ")}</h3>
        <h3>三連號: ${data.three_streaks.map(t => t[0].join("-")).join(", ")}</h3>
        <h3>四連號: ${data.four_streaks.map(t => t[0].join("-")).join(", ")}</h3>
        <h3>熱門頭號: ${data.hot_heads.join(", ")}</h3>
        <h3>熱門尾號: ${data.hot_tails.join(", ")}</h3>
        <h3>二同出: ${data.two_same.map(t => t[0].join("-")).join(", ")}</h3>
        <h3>三同出: ${data.three_same.map(t => t[0].join("-")).join(", ")}</h3>
    `;

    document.getElementById("statistics").innerHTML = statsHtml;
}

createNumberGrid();
