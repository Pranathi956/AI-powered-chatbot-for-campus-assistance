document.addEventListener("DOMContentLoaded", function () {
  const botFailureChart = new Chart(document.getElementById('botFailureChart'), {
    type: 'doughnut',
    data: {
      labels: ['Bot Failed (Admin Escalation)', 'Bot Handled'],
      datasets: [{
        data: [
          parseFloat(document.getElementById("botFailureChart").dataset.failure),
          parseFloat(document.getElementById("botFailureChart").dataset.handled)
        ],
        backgroundColor: ['#dc2626', '#22c55e']
      }]
    },
    options: {
      plugins: {
        title: {
          display: true,
          text: 'Bot Failure-to-Answer Rate (%)'
        },
        legend: {
          position: 'bottom'
        },
        tooltip: {
          callbacks: {
            label: function (context) {
              return context.label + ': ' + context.parsed.toFixed(1) + '%';
            }
          }
        }
      }
    }
  });
});
