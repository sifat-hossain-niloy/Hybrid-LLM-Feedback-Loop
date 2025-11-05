// ===== Smooth Scroll for Navigation =====
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// ===== Chart.js Configuration =====
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.color = '#64748b';

// ===== ICPC Pass Rate Chart =====
const icpcCtx = document.getElementById('icpcPassRateChart');
if (icpcCtx) {
    new Chart(icpcCtx, {
        type: 'bar',
        data: {
            labels: ['GPT-5 + DeepSeek', 'GPT-5 + Llama', 'GPT-5 + Codestral', 
                     'GPT-4 + DeepSeek', 'GPT-4 + Llama', 'GPT-4 + Codestral'],
            datasets: [
                {
                    label: 'Pass@0 (Zero-shot)',
                    data: [39, 39, 39, 15, 15, 15],
                    backgroundColor: 'rgba(99, 102, 241, 0.6)',
                    borderColor: 'rgba(99, 102, 241, 1)',
                    borderWidth: 2
                },
                {
                    label: 'Pass@1',
                    data: [64, 59, 61, 22, 19, 18],
                    backgroundColor: 'rgba(139, 92, 246, 0.6)',
                    borderColor: 'rgba(139, 92, 246, 1)',
                    borderWidth: 2
                },
                {
                    label: 'Pass@2',
                    data: [79, 73, 78, 30, 26, 24],
                    backgroundColor: 'rgba(236, 72, 153, 0.6)',
                    borderColor: 'rgba(236, 72, 153, 1)',
                    borderWidth: 2
                },
                {
                    label: 'Pass@3',
                    data: [90, 87, 85, 38, 34, 31],
                    backgroundColor: 'rgba(16, 185, 129, 0.6)',
                    borderColor: 'rgba(16, 185, 129, 1)',
                    borderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                title: {
                    display: true,
                    text: 'ICPC World Finals: Pass@k Performance (167 problems)',
                    font: { size: 16, weight: 'bold' }
                },
                legend: {
                    position: 'top',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            label += context.parsed.y + '/167';
                            return label;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value;
                        }
                    },
                    title: {
                        display: true,
                        text: 'Problems Solved'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Workflow Combination'
                    }
                }
            }
        }
    });
}

// ===== Codeforces Pass Rate Chart =====
const cfCtx = document.getElementById('codeforcesPassRateChart');
if (cfCtx) {
    new Chart(cfCtx, {
        type: 'line',
        data: {
            labels: ['Pass@0', 'Pass@1', 'Pass@2', 'Pass@3'],
            datasets: [
                {
                    label: 'GPT-5 + DeepSeek',
                    data: [22.0, 43.0, 52.5, 41.0],
                    borderColor: 'rgba(16, 185, 129, 1)',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 3,
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    tension: 0.3,
                    fill: true
                },
                {
                    label: 'GPT-5 + Llama',
                    data: [22.5, 45.0, 53.5, 37.0],
                    borderColor: 'rgba(139, 92, 246, 1)',
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
                    borderWidth: 3,
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    tension: 0.3,
                    fill: true
                },
                {
                    label: 'GPT-5 + Codestral',
                    data: [20.5, 42.0, 49.5, 34.0],
                    borderColor: 'rgba(99, 102, 241, 1)',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    borderWidth: 3,
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    tension: 0.3,
                    fill: true
                },
                {
                    label: 'GPT-4 + DeepSeek',
                    data: [10.0, 19.0, 26.0, 26.0],
                    borderColor: 'rgba(16, 185, 129, 0.6)',
                    backgroundColor: 'rgba(16, 185, 129, 0.05)',
                    borderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    tension: 0.3,
                    fill: true,
                    borderDash: [5, 5]
                },
                {
                    label: 'GPT-4 + Llama',
                    data: [10.5, 21.0, 26.5, 23.5],
                    borderColor: 'rgba(139, 92, 246, 0.6)',
                    backgroundColor: 'rgba(139, 92, 246, 0.05)',
                    borderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    tension: 0.3,
                    fill: true,
                    borderDash: [5, 5]
                },
                {
                    label: 'GPT-4 + Codestral',
                    data: [9.0, 18.0, 22.5, 21.0],
                    borderColor: 'rgba(99, 102, 241, 0.6)',
                    backgroundColor: 'rgba(99, 102, 241, 0.05)',
                    borderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    tension: 0.3,
                    fill: true,
                    borderDash: [5, 5]
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Codeforces: Pass@k Rate Evolution (200 problems, rating 1200-1800)',
                    font: { size: 16, weight: 'bold' }
                },
                legend: {
                    position: 'top',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.parsed.y.toFixed(1) + '%';
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 60,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    },
                    title: {
                        display: true,
                        text: 'Success Rate (%)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Refinement Iteration'
                    }
                }
            }
        }
    });
}

// ===== SOTA Comparison Chart =====
const sotaCtx = document.getElementById('sotaComparisonChart');
if (sotaCtx) {
    new Chart(sotaCtx, {
        type: 'bar',
        data: {
            labels: ['GPT-5 + DeepSeek\n(Ours)', 'AlphaCode 2', 'GPT-5 + Llama\n(Ours)', 
                     'GPT-5 + Codestral\n(Ours)', 'AlphaCode 1', 'GPT-4 + DeepSeek\n(Ours)'],
            datasets: [{
                label: 'Pass@3 / Success Rate',
                data: [41.0, 43.0, 37.0, 34.0, 34.0, 26.0],
                backgroundColor: [
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(239, 68, 68, 0.6)',
                    'rgba(139, 92, 246, 0.8)',
                    'rgba(99, 102, 241, 0.8)',
                    'rgba(239, 68, 68, 0.4)',
                    'rgba(59, 130, 246, 0.8)'
                ],
                borderColor: [
                    'rgba(16, 185, 129, 1)',
                    'rgba(239, 68, 68, 1)',
                    'rgba(139, 92, 246, 1)',
                    'rgba(99, 102, 241, 1)',
                    'rgba(239, 68, 68, 1)',
                    'rgba(59, 130, 246, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            indexAxis: 'y',
            plugins: {
                title: {
                    display: true,
                    text: 'Comparison with State-of-the-Art Systems',
                    font: { size: 16, weight: 'bold' }
                },
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.parsed.x.toFixed(1) + '% success';
                            if (context.label.includes('(Ours)')) {
                                label += ' (3 attempts)';
                            } else {
                                label += ' (1M samples)';
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    max: 50,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    },
                    title: {
                        display: true,
                        text: 'Success Rate (%)'
                    }
                }
            }
        }
    });
}

// ===== Critic Comparison Chart =====
const criticCtx = document.getElementById('criticComparisonChart');
if (criticCtx) {
    new Chart(criticCtx, {
        type: 'radar',
        data: {
            labels: ['ICPC Pass@0', 'ICPC Pass@3', 'CF Pass@3', 'Improvement %', 'Avg Attempts'],
            datasets: [
                {
                    label: 'DeepSeek-R1',
                    data: [27, 64, 33.5, 135, 90],
                    backgroundColor: 'rgba(16, 185, 129, 0.2)',
                    borderColor: 'rgba(16, 185, 129, 1)',
                    pointBackgroundColor: 'rgba(16, 185, 129, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(16, 185, 129, 1)',
                    borderWidth: 3
                },
                {
                    label: 'Llama-3.3-70B',
                    data: [27, 60.5, 30.25, 125, 88],
                    backgroundColor: 'rgba(139, 92, 246, 0.2)',
                    borderColor: 'rgba(139, 92, 246, 1)',
                    pointBackgroundColor: 'rgba(139, 92, 246, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(139, 92, 246, 1)',
                    borderWidth: 3
                },
                {
                    label: 'Codestral-2508',
                    data: [27, 58, 27.5, 112.5, 85],
                    backgroundColor: 'rgba(99, 102, 241, 0.2)',
                    borderColor: 'rgba(99, 102, 241, 1)',
                    pointBackgroundColor: 'rgba(99, 102, 241, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(99, 102, 241, 1)',
                    borderWidth: 3
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Debugging Critic Performance Comparison (Averaged Across Generators)',
                    font: { size: 16, weight: 'bold' }
                },
                legend: {
                    position: 'top'
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    max: 150,
                    ticks: {
                        stepSize: 30
                    }
                }
            }
        }
    });
}

// ===== Scroll Animations =====
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

document.querySelectorAll('.overview-card, .rq-card, .metric-card, .insight-card, .comparison-card').forEach((el) => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(el);
});

// ===== Active Navigation Highlighting =====
window.addEventListener('scroll', () => {
    let current = '';
    const sections = document.querySelectorAll('section[id]');
    
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        if (pageYOffset >= sectionTop - 200) {
            current = section.getAttribute('id');
        }
    });

    document.querySelectorAll('.nav-menu a').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${current}`) {
            link.classList.add('active');
        }
    });
});

