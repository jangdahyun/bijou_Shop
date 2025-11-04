document.addEventListener("DOMContentLoaded", () => {
  const salesDataElement = document.getElementById("weekly-sales-data");
  const categoryDataElement = document.getElementById("weekly-category-data");

  if (!salesDataElement && !categoryDataElement) {
    return;
  }

  const parseJSON = (element) => {
    if (!element) {
      return [];
    }
    try {
      return JSON.parse(element.textContent);
    } catch (err) {
      console.warn("Failed to parse dashboard JSON payload.", err);
      return [];
    }
  };

  const weeklySales = parseJSON(salesDataElement);
  const weeklyCategory = parseJSON(categoryDataElement);

  const salesCanvas = document.getElementById("weeklySalesChart");
  if (salesCanvas && weeklySales.length) {
    const salesLabels = weeklySales.map((item) => item.label);
    const salesTotals = weeklySales.map((item) => item.total);

    new Chart(salesCanvas, {
      type: "line",
      data: {
        labels: salesLabels,
        datasets: [
          {
            label: "₩",
            data: salesTotals,
            borderColor: "#f9d74c",
            backgroundColor: "rgba(249, 215, 76, 0.18)",
            borderWidth: 3,
            tension: 0.35,
            fill: true,
            pointRadius: 4,
            pointBackgroundColor: "#f9d74c",
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            callbacks: {
              label(context) {
                const value = context.parsed.y || 0;
                return `₩ ${value.toLocaleString()}`;
              },
            },
          },
        },
        scales: {
          x: {
            ticks: {
              color: "#9da0a9",
            },
            grid: {
              color: "rgba(255,255,255,0.06)",
            },
          },
          y: {
            ticks: {
              color: "#9da0a9",
              callback(value) {
                return `₩${Number(value).toLocaleString()}`;
              },
            },
            grid: {
              color: "rgba(255,255,255,0.06)",
            },
          },
        },
      },
    });
  }

  const categoryCanvas = document.getElementById("categoryChart");
  const categoryEmptyState = document.querySelector(".chart-card__empty");

  if (categoryCanvas) {
    if (weeklyCategory.length) {
      const categoryLabels = weeklyCategory.map((item) => item.label);
      const categoryValues = weeklyCategory.map((item) => item.value);
      const palette = [
        "#f9d74c",
        "#7b8dff",
        "#f04e37",
        "#6ce5b1",
        "#ffa3a3",
        "#7bdff2",
        "#b28dff",
      ];

      new Chart(categoryCanvas, {
        type: "doughnut",
        data: {
          labels: categoryLabels,
          datasets: [
            {
              data: categoryValues,
              backgroundColor: categoryValues.map(
                (_, index) => palette[index % palette.length]
              ),
              borderWidth: 0,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: "bottom",
              labels: {
                color: "#9da0a9",
                usePointStyle: true,
              },
            },
            tooltip: {
              callbacks: {
                label(context) {
                  const value = context.parsed || 0;
                  return `${context.label}: ₩${Number(value).toLocaleString()}`;
                },
              },
            },
          },
          cutout: "58%",
        },
      });
    } else if (categoryEmptyState) {
      categoryEmptyState.hidden = false;
    }
  }
});
