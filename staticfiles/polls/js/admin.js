document.addEventListener('DOMContentLoaded', function() {
    // Store charts to update them later
    const charts = {};
    
    // Function to fetch results and update charts
    function updateResults() {
        fetch('/get-results/')
            .then(response => response.json())
            .then(data => {
                data.forEach(position => {
                    const positionId = position.position.replace(/\s+/g, '-').toLowerCase();
                    const resultsTableBody = document.querySelector(`#results-${positionId}`);
                    
                    if (resultsTableBody) {
                        // Clear existing results
                        resultsTableBody.innerHTML = '';
                        
                        // Add new results
                        position.candidates.forEach(candidate => {
                            const row = document.createElement('tr');
                            row.innerHTML = `
                                <td>${candidate.name}</td>
                                <td>${candidate.votes}</td>
                            `;
                            resultsTableBody.appendChild(row);
                        });
                        
                        // Update chart if it exists
                        if (charts[positionId]) {
                            updateChart(charts[positionId], position.candidates);
                        } else {
                            // Create new chart
                            const ctx = document.getElementById(`chart-${positionId}`);
                            if (ctx) {
                                charts[positionId] = createChart(ctx, position);
                            }
                        }
                    }
                });
            })
            .catch(error => console.error('Error fetching results:', error));
    }
    
    // Function to create a new chart
    function createChart(ctx, position) {
        const labels = position.candidates.map(c => c.name);
        const data = position.candidates.map(c => c.votes);
        const backgroundColors = generateColors(position.candidates.length);
        
        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Votes',
                    data: data,
                    backgroundColor: backgroundColors,
                    borderColor: backgroundColors.map(color => color.replace('0.6', '1')),
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
    }
    
    // Function to update an existing chart
    function updateChart(chart, candidates) {
        chart.data.datasets[0].data = candidates.map(c => c.votes);
        chart.update();
    }
    
    // Function to generate random colors
    function generateColors(count) {
        const colors = [];
        for (let i = 0; i < count; i++) {
            const hue = (i * 137) % 360; // Use golden angle to get evenly distributed colors
            colors.push(`hsla(${hue}, 70%, 60%, 0.6)`);
        }
        return colors;
    }
    
    // Initial update
    updateResults();
    
    // Update every minute
    setInterval(updateResults, 60000);
});