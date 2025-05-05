const diasSemana = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];

    
const fechasNumeros = JSON.parse(document.getElementById('fechas-data').textContent);
const fechas = Array.isArray(fechasNumeros) ? fechasNumeros.map(n => diasSemana[n]) : [];

const ingresos = JSON.parse(document.getElementById('ingresos-data').textContent);
const ventas = JSON.parse(document.getElementById('ventas-data').textContent);


new Chart(document.getElementById('ingresosChart').getContext('2d'), {
    type: 'line',
    data: {
        labels: fechas,
        datasets: [{
            label: 'Ingresos',
            data: ingresos,
            backgroundColor: '#4cbd667a',
            borderColor: '#4cbd66',
            borderWidth: 1
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: {
                grid: { display: false },
                ticks: {
                    maxRotation: 45,
                    minRotation: 45,
                    autoSkip: false
                }
            },
            y: {
                beginAtZero: true,
                max: 50000,
                grid: { display: false },
                ticks: {
                    callback: value => `$${value.toLocaleString()}`
                }
            }
        },
        plugins: {
            legend: { display: false }
        }
    }
});


new Chart(document.getElementById('ventasChart').getContext('2d'), {
    type: 'bar',
    data: {
        labels: fechas,
        datasets: [{
            label: 'Reservas',
            data: ventas,
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 4,
            fill: true,
            tension: 0.3
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: {
                grid: { display: false },
                ticks: {
                    maxRotation: 45,
                    minRotation: 45,
                    autoSkip: false
                }
            },
            y: {
                beginAtZero: true,
                grid: { display: false },
                ticks: {
                    precision: 0
                }
            }
        },
        plugins: {
            legend: { display: false }
        }
    }
});