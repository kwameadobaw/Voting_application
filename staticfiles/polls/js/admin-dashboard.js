document.addEventListener('DOMContentLoaded', function() {
    // Store charts to update them later
    const charts = {};
    
    // Function to initialize charts
    function initializeCharts() {
        const positions = document.querySelectorAll('.position-card');
        
        positions.forEach(position => {
            const canvasId = position.querySelector('canvas').id;
            const positionId = canvasId.split('-')[1];
            
            // Get candidates and votes from the DOM
            const candidateRows = position.querySelectorAll('.results-table tbody tr');
            const labels = [];
            const data = [];
            
            candidateRows.forEach(row => {
                if (row.cells.length >= 2) {
                    labels.push(row.cells[0].textContent);
                    data.push(parseInt(row.cells[1].textContent) || 0);
                }
            });
            
            // Create chart
            const ctx = document.getElementById(canvasId).getContext('2d');
            charts[positionId] = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Votes',
                        data: data,
                        backgroundColor: [
                            'rgba(54, 162, 235, 0.6)',
                            'rgba(255, 99, 132, 0.6)',
                            'rgba(255, 206, 86, 0.6)',
                            'rgba(75, 192, 192, 0.6)',
                            'rgba(153, 102, 255, 0.6)',
                            'rgba(255, 159, 64, 0.6)'
                        ],
                        borderColor: [
                            'rgba(54, 162, 235, 1)',
                            'rgba(255, 99, 132, 1)',
                            'rgba(255, 206, 86, 1)',
                            'rgba(75, 192, 192, 1)',
                            'rgba(153, 102, 255, 1)',
                            'rgba(255, 159, 64, 1)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                precision: 0
                            }
                        }
                    }
                }
            });
        });
    }
    
    // Function to update charts with new data
    function updateCharts() {
        fetch('/api/voting-data/')
            .then(response => response.json())
            .then(data => {
                data.forEach(position => {
                    const positionTitle = position.position.replace(/\s+/g, '-').toLowerCase();
                    const chart = charts[positionTitle];
                    
                    if (chart) {
                        // Update chart data
                        chart.data.labels = position.candidates.map(c => c.name);
                        chart.data.datasets[0].data = position.candidates.map(c => c.votes);
                        chart.update();
                        
                        // Update table data
                        const tableBody = document.querySelector(`#results-${positionTitle}`);
                        if (tableBody) {
                            tableBody.innerHTML = '';
                            position.candidates.forEach(candidate => {
                                const row = document.createElement('tr');
                                row.innerHTML = `
                                    <td>${candidate.name}</td>
                                    <td>${candidate.votes}</td>
                                `;
                                tableBody.appendChild(row);
                            });
                        }
                    }
                });
            })
            .catch(error => console.error('Error updating charts:', error));
    }
    
    // Initialize charts
    initializeCharts();
    
    // Update charts every minute
    setInterval(updateCharts, 60000);
});