from flask import Flask, render_template_string, jsonify
import requests

app = Flask(__name__)

TEMPLATE = """
<!doctype html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <title>Fraud Alerts Dashboard</title>
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .high-risk-row td {
            background-color: #ff4d4d !important;
            color: #fff !important;
        }
        .fraud-row td {
            background-color: #ffe5e5 !important;
        }
    </style>
</head>
<body class="bg-light">
<div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-3">
        <h2>Дашборд мошеннических транзакций</h2>
        <span id="last-update" class="badge bg-primary"></span>
    </div>
    <div class="row g-4 mb-4">
        <div class="col-md-2">
            <div class="card text-center border-danger">
                <div class="card-body">
                    <h6 class="card-title">Мошеннические транзакции</h6>
                    <span id="stat-total" class="fs-4 fw-bold text-danger"></span>
                </div>
            </div>
        </div>
        <div class="col-md-2">
            <div class="card text-center border-info">
                <div class="card-body">
                    <h6 class="card-title">Ср. вероятность</h6>
                    <span id="stat-avgprob" class="fs-4"></span>
                </div>
            </div>
        </div>
        <div class="col-md-2">
            <div class="card text-center border-success">
                <div class="card-body">
                    <h6 class="card-title">Сред. сумма</h6>
                    <span id="stat-avgamt" class="fs-4"></span>
                </div>
            </div>
        </div>
        <div class="col-md-2">
            <div class="card text-center border-warning">
                <div class="card-body">
                    <h6 class="card-title">Макс. сумма</h6>
                    <span id="stat-maxamt" class="fs-4"></span>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card text-center border-secondary">
                <div class="card-body">
                    <h6 class="card-title">Последняя операция</h6>
                    <span id="stat-lasttime" class="fs-6"></span>
                </div>
            </div>
        </div>
    </div>
    <div class="row mb-4">
        <div class="col-md-8">
            <canvas id="fraudChart" height="100"></canvas>
        </div>
        <div class="col-md-4">
            <div class="alert alert-info">
                График: динамика вероятности мошенничества по времени<br>
            </div>
        </div>
    </div>
    <div>
        <h5>Последние мошеннические транзакции</h5>
        <table class="table table-bordered">
            <thead class="table-dark">
                <tr>
                    <th>Время</th>
                    <th>Сумма</th>
                    <th>Вероятность</th>
                    <th>Prediction</th>
                    <th>Class</th>
                </tr>
            </thead>
            <tbody id="table-body">
            </tbody>
        </table>
    </div>
</div>

<script>
let chart;
function renderChart(data) {
    const times = data.map(x => x.time);
    const probs = data.map(x => x.fraud_probability);
    if (!chart) {
        const ctx = document.getElementById('fraudChart').getContext('2d');
        chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: times,
                datasets: [{
                    label: 'Fraud Probability',
                    data: probs,
                    fill: false,
                    tension: 0.15,
                    borderColor: 'rgb(255, 99, 132)',
                    pointRadius: 3,
                }]
            },
            options: {
                animation: false,
                responsive: true,
                scales: {
                    x: {title: {display: true, text: 'Time'}},
                    y: {min: 0, max: 1, title: {display: true, text: 'Probability'}}
                }
            }
        });
    } else {
        chart.data.labels = times;
        chart.data.datasets[0].data = probs;
        chart.update();
    }
}

function renderTable(data) {
    let html = '';
    data.slice().reverse().forEach(row => {
        const isHighRisk = row.fraud_probability > 0.80;
        html += `<tr class="${isHighRisk ? 'high-risk-row' : 'fraud-row'}">
            <td>${row.time}</td>
            <td>${row.amount}</td>
            <td>${row.fraud_probability.toFixed(3)}</td>
            <td>${row.prediction}</td>
            <td>${row.clazz}</td>
        </tr>`;
    });
    document.getElementById('table-body').innerHTML = html;
}

function renderStats(data, total) {
    if (!data.length) return;
    let sum = 0, sumprob = 0, maxamt = 0;
    let lastTime = 0;
    data.forEach(row => {
        sum += row.amount;
        sumprob += row.fraud_probability;
        if (row.amount > maxamt) maxamt = row.amount;
        if (row.time > lastTime) lastTime = row.time;
    });
    document.getElementById('stat-total').textContent = total;
    document.getElementById('stat-avgprob').textContent = (sumprob / data.length).toFixed(2);
    document.getElementById('stat-avgamt').textContent = (sum / data.length).toFixed(2);
    document.getElementById('stat-maxamt').textContent = maxamt.toFixed(2);
    document.getElementById('stat-lasttime').textContent = lastTime;
}

function updateData() {
    fetch('/fraud_data')
        .then(resp => resp.json())
        .then(obj => {
            let data = obj.last;
            renderChart(data);
            renderTable(data);
            renderStats(data, obj.total_count);
            document.getElementById('last-update').textContent =
                'Обновлено: ' + (new Date()).toLocaleTimeString();
        });
}
setInterval(updateData, 3000);
window.onload = updateData;
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(TEMPLATE)

@app.route("/fraud_data")
def fraud_data():
    try:
        resp = requests.get("http://localhost:5000/fraud", timeout=2)
        data = resp.json()
    except Exception:
        data = []
    total_count = len(data)
    data_last = sorted(data, key=lambda x: x.get("time", 0))[-50:]
    return jsonify({"total_count": total_count, "last": data_last})

if __name__ == "__main__":
    app.run(port=8000, debug=True)
