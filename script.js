function learnMore() {
  alert("This AI-powered tool analyzes resumes, extracts skills, and compares them with job descriptions for smart insights.");
}

// Handle form submission with AJAX
document.querySelector("form").addEventListener("submit", async function(e) {
  e.preventDefault();
  const formData = new FormData(this);

  const response = await fetch("/analyze", {
    method: "POST",
    body: formData
  });

  const data = await response.json();
  renderCharts(data);
});

// Render charts
function renderCharts(data) {
  // Score chart
  new Chart(document.getElementById("scoreChart"), {
    type: "doughnut",
    data: {
      labels: ["Score", "Remaining"],
      datasets: [{
        data: [data.score, 100 - data.score],
        backgroundColor: ["#ff6a00", "#ddd"]
      }]
    },
    options: {
      plugins: {
        title: {
          display: true,
          text: "Resume Score"
        }
      }
    }
  });

  // Job match chart
  new Chart(document.getElementById("matchChart"), {
    type: "bar",
    data: {
      labels: ["Job Match %"],
      datasets: [{
        label: "Match",
        data: [data.similarity],
        backgroundColor: "#2575fc"
      }]
    },
    options: {
      plugins: {
        title: {
          display: true,
          text: "Resume-Job Match"
        }
      },
      scales: {
        y: { beginAtZero: true, max: 100 }
      }
    }
  });
}
