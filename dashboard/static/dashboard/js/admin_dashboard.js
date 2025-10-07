document.addEventListener("DOMContentLoaded", function () {
    const canvas = document.getElementById("reservationsChart");
    if (!canvas) return;

    const labels = JSON.parse(canvas.dataset.labels);
    const values = JSON.parse(canvas.dataset.values);

    const ctx = canvas.getContext("2d");

    new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: "تعداد رزروها",
                data: values,
                fill: true,
                borderColor: "#4e73df",
                backgroundColor: "rgba(78, 115, 223, 0.2)",
                tension: 0.3,
                pointRadius: 4,
                pointHoverRadius: 6,
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                tooltip: { rtl: true }
            },
            scales: {
                x: {
                    ticks: { font: { family: "Vazir, sans-serif" } }
                },
                y: {
                    beginAtZero: true,
                    ticks: { stepSize: 1 }
                }
            }
        }
    });
});
