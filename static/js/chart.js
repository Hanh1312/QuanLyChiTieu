// ============================
// TOTAL EXPENSE
// ============================

let totalExpense = 0;

chartValues.forEach((value) => {
  totalExpense += Number(value);
});

const totalElement = document.getElementById("totalExpense");

if (totalElement) {
  totalElement.innerHTML = totalExpense.toLocaleString("vi-VN") + " đ";
}

// ============================
// BAR CHART
// ============================

const expenseCanvas = document.getElementById("expenseChart");

if (expenseCanvas) {
  new Chart(expenseCanvas, {
    type: "bar",

    data: {
      labels: chartMonths,

      datasets: [
        {
          label: "Chi tiêu",

          data: chartValues,

          backgroundColor: [
            "#ffc8dd",
            "#ffcad4",
            "#fde2e4",
            "#fad2e1",
            "#cdb4db",
            "#d8e2dc",
            "#bee1e6",
            "#a2d2ff",
            "#bde0fe",
            "#d8f3dc",
            "#ffe5b4",
            "#f8edeb",
          ],

          borderRadius: 10,
        },
      ],
    },

    options: {
      responsive: true,

      plugins: {
        legend: {
          display: false,
        },
      },

      scales: {
        y: {
          beginAtZero: true,
        },
      },
    },
  });
}

// ============================
// PIE CHART
// ============================

const pieCanvas = document.getElementById("pieChart");

if (pieCanvas) {
  new Chart(pieCanvas, {
    type: "pie",

    data: {
      labels: chartMonths,

      datasets: [
        {
          data: chartValues,

          backgroundColor: [
            "#ffc8dd",
            "#ffcad4",
            "#fde2e4",
            "#fad2e1",
            "#cdb4db",
            "#d8e2dc",
            "#bee1e6",
            "#a2d2ff",
            "#bde0fe",
            "#d8f3dc",
            "#ffe5b4",
            "#f8edeb",
          ],
        },
      ],
    },

    options: {
      responsive: true,
      maintainAspectRatio: false,
    },
  });
}
