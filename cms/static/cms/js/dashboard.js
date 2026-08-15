const revenueChartDataSets = {
    today: {
        labels: ["9 AM", "12 PM", "3 PM", "6 PM", "9 PM"],
        confirmed: [15000, 45000, 80000, 120000, 150000],
        projected: [20000, 55000, 95000, 140000, 185000]
    },
    week: {
        labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        confirmed: [30000, 45000, 60000, 75000, 90000, 140000, 180000],
        projected: [38000, 58000, 75000, 95000, 115000, 175000, 220000]
    },
    month: {
        labels: ["Week 1", "Week 2", "Week 3", "Week 4"],
        confirmed: [120000, 190000, 240000, 310000],
        projected: [150000, 230000, 300000, 390000]
    },
    year: {
        labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        confirmed: [25000, 40000, 35000, 50000, 65000, 70000, 85000, 95000, 110000, 130000, 155000, 180000],
        projected: [32000, 50000, 45000, 65000, 82000, 90000, 110000, 125000, 140000, 165000, 195000, 230000]
    },
    all: {
        labels: ["2022", "2023", "2024", "2025", "2026"],
        confirmed: [450000, 890000, 1450000, 2100000, 2835668],
        projected: [520000, 1050000, 1700000, 2500000, 3544585]
    }
};

document.addEventListener("DOMContentLoaded", function () {
    const ctx = document.getElementById("revenueChart");

    if (ctx) {
        window.revenueChartInstance = new Chart(ctx, {
            type: "line",
            data: {
                labels: revenueChartDataSets.month.labels,
                datasets: [
                    {
                        label: "Confirmed Revenue",
                        data: revenueChartDataSets.month.confirmed,
                        borderColor: "#171717",
                        backgroundColor: "rgba(23,23,23,0.06)",
                        fill: true,
                        tension: 0.4,
                        pointRadius: 4,
                        pointBackgroundColor: "#171717"
                    },
                    {
                        label: "Projected (Confirmed + Pending)",
                        data: revenueChartDataSets.month.projected,
                        borderColor: "#71717a",
                        borderDash: [5, 5],
                        backgroundColor: "transparent",
                        fill: false,
                        tension: 0.4,
                        pointRadius: 3,
                        pointBackgroundColor: "#71717a"
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(val) {
                                return '₹ ' + val.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }
});

function updateRevenueChart(period, btnElement) {
    if (!window.revenueChartInstance || !revenueChartDataSets[period]) return;

    const dataSet = revenueChartDataSets[period];
    window.revenueChartInstance.data.labels = dataSet.labels;
    window.revenueChartInstance.data.datasets[0].data = dataSet.confirmed;
    window.revenueChartInstance.data.datasets[1].data = dataSet.projected;
    window.revenueChartInstance.update();

    const buttons = document.querySelectorAll(".chart-filter-btn");
    buttons.forEach(btn => btn.classList.remove("active"));
    if (btnElement) {
        btnElement.classList.add("active");
    }
}

function toggleVenueStatus(url, checkbox) {

    const previousState = checkbox.checked;

    fetch(url, {
        method: "POST",
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCookie("csrftoken"),
            "Content-Type": "application/json"
        }
    })
    .then(async response => {

        const data = await response.json();

        if (!response.ok || data.status !== "success") {
            throw new Error(
                data.message || "Unable to update hall status."
            );
        }

        console.log("Hall status updated:", data);

    })
    .catch(error => {

        console.error("Toggle error:", error);

        // Roll back checkbox if request failed
        checkbox.checked = previousState;

        alert("Unable to update hall status.");
    });
}

/* =========================================
   EXPO DESIGN FULL IMAGE MODAL HANDLERS
   ========================================= */
function openFullImageModal(imageUrl, title = "Banner Image Preview") {
    if (!imageUrl) return;
    const modal = document.getElementById("expoImageModal");
    const modalImg = document.getElementById("expoModalImage");
    const modalTitle = document.getElementById("expoModalTitle");
    const downloadBtn = document.getElementById("expoModalDownloadBtn");

    if (!modal || !modalImg) return;

    modalImg.src = imageUrl;
    if (modalTitle) modalTitle.textContent = title;
    if (downloadBtn) downloadBtn.href = imageUrl;

    modal.classList.add("active");
    document.body.style.overflow = "hidden";
}

function closeFullImageModal(event) {
    if (event && event.target !== event.currentTarget && !event.target.closest('.expo-modal-close')) {
        return;
    }
    const modal = document.getElementById("expoImageModal");
    if (modal) {
        modal.classList.remove("active");
    }
    document.body.style.overflow = "";
}

document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
        closeFullImageModal();
    }
});
