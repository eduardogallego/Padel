let chartId;
let chart25Id;
let chartYearId;
let monthsId;
let lastResult;
let last25Result;
let lastYearResult;

function cellStylePartnerResult(value, row, index) {
    let result = '';
    let sum = row.pw - row.pl;
    if (sum > 0) {
        result = 'win';
    } else if (sum < 0) {
        result = 'loss';
    } else if ((row.pw + row.pd + row.pl) > 0) {
        result = 'draw';
    }
    return {
        classes: result
    }
}

function cellStylePlayerResult(value, row, index) {
    let result = '';
    let sum = row.pw + row.rw - row.pl - row.rl;
    if (sum > 0) {
        result = 'win';
    } else if (sum < 0) {
        result = 'loss';
    } else if (row.total > 0) {
        result = 'draw';
    }
    return {
        classes: result
    }
}

function cellStyleIndexPlayerResult(value, row, index) {
    let result = '';
    let sum = row.pw + row.rw - row.pl - row.rl;
    if (sum > 0) {
        result = 'win';
    } else if (sum < 0) {
        result = 'loss';
    } else if (row.total > 0) {
        result = 'draw';
    }
    return {
        classes: 'index ' + result
    }
}

function cellStyleRivalResult(value, row, index) {
    let result = '';
    let sum = row.rw - row.rl;
    if (sum > 0) {
        result = 'win';
    } else if (sum < 0) {
        result = 'loss';
    } else if ((row.rw + row.rd + row.rl) > 0) {
        result = 'draw';
    }
    return {
        classes: result
    }
}

function cellStyleIndexMatchResult(value, row, index) {
    let result = 'draw';
    if (row.result != null) {
        result = row.result === 1 ? 'win' : 'loss';
    }
    return {
        classes: 'index ' + result
    }
}

function cellStyleMatchResult(value, row, index) {
    let result = 'draw';
    if (row.result != null) {
        result = row.result === 1 ? 'win' : 'loss';
    }
    return {
        classes: result
    }
}

function footItemCountFormatter(data) {
    return data.length;
}

function footResults(data) {
    let win = 0;
    let loss = 0;
    let draw = 0;
    const yearMap = new Map();
    let years = []
    data.forEach(function(data) {
        const dateTokens = data.date.split("-");
        let resultMap;
        if (yearMap.has(dateTokens[0])) {
            resultMap = yearMap.get(dateTokens[0]);
        } else {
            resultMap = new Map([['win', [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]],
                ['draw', [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], ['loss', [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]]);
            yearMap.set(dateTokens[0], resultMap);
            years.push(dateTokens[0]);
        }
        let id = parseInt(dateTokens[1]) - 1;
        if (data.result == null) {
            draw += 1;
            resultMap.get('draw')[id] += 1;
        } else if (data.result === 1) {
            win += 1;
            resultMap.get('win')[id] += 1;
        } else {
            loss += 1;
            resultMap.get('loss')[id] += 1;
        }
    });
    let result = win + "/" + draw + "/" + loss;
    if (lastResult !== result) {
        let chart = document.getElementById("chartId").getContext("2d");
        let total = win + draw + loss;
        if (chartId) {
            chartId.destroy()
        }
        chartId = new Chart(chart, {
            type: 'pie',
            data: {
                labels: ["win", "draw", "loss"],
                datasets: [{
                    data: [(win * 100 / total).toFixed(1), (draw * 100 / total).toFixed(1),
                    (loss * 100 / total).toFixed(1)],
                    backgroundColor: ['MediumSeaGreen', 'Orange', 'Tomato'],
                    hoverOffset: 5
                }],
            },
            options: {
                responsive: false,
                plugins: {
                    legend: {
                        display: true,
                        position: "bottom",
                        align: "center"
                    }
                }
            }
        });
        let timeseries = document.getElementById("monthsId").getContext("2d");
        if (monthsId) {
            monthsId.destroy()
        }
        monthsId = new Chart(timeseries, {
            type: 'bar',
            data: {
                labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July',
                    'August', 'September', 'October', 'November', 'December'],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: { stacked: true },
                    y: { stacked: true }
                }
            }
        });
        years.sort().forEach(function (year, index) {
            monthsId.data.datasets.push({
                label: 'loss_' + year,
                data: yearMap.get(year).get('loss'),
                backgroundColor: 'Tomato',
                stack: year
            });
            monthsId.data.datasets.push({
                label: 'draw_' + year,
                data: yearMap.get(year).get('draw'),
                backgroundColor: 'Orange',
                stack: year
            });
            monthsId.data.datasets.push({
                label: 'win_' + year,
                data: yearMap.get(year).get('win'),
                backgroundColor: 'MediumSeaGreen',
                stack: year
            });
        })
        monthsId.update();
        lastResult = result;
    }
    return result;
}

function foot25Results(data) {
    let win = 0;
    let loss = 0
    let draw = 0;
    let counter = 0;
    data.forEach(function(data) {
        if (counter < 25) {
            if (data.result == null) {
                draw += 1;
            } else if (data.result === 1) {
                win += 1;
            } else {
                loss += 1;
            }
        }
        counter += 1;
    });
    result = win + "/" + draw + "/" + loss;
    if (last25Result !== result) {
        let chart = document.getElementById("chart25Id").getContext("2d");
        let total = win + draw + loss;
        if (chart25Id) {
            chart25Id.destroy()
        }
        chart25Id = new Chart(chart, {
            type: 'pie',
            data: {
                labels: ["win", "draw", "loss"],
                datasets: [{
                    data: [(win * 100 / total).toFixed(1), (draw * 100 / total).toFixed(1),
                    (loss * 100 / total).toFixed(1)],
                    backgroundColor: ['MediumSeaGreen', 'Orange', 'Tomato'],
                    hoverOffset: 5
                }],
            },
            options: {
                responsive: false,
                plugins: {
                    legend: {
                        display: true,
                        position: "bottom",
                        align: "center"
                    }
                }
            }
        });
        last25Result = result;
    }
    return result;
}

function footYearResults(data) {
    let win = 0;
    let loss = 0
    let draw = 0;
    let counter = 0;
    let currentYear = (new Date()).getUTCFullYear();
    data.forEach(function(data) {
        let matchYear = (new Date(data.date)).getUTCFullYear();
        if (matchYear === currentYear) {
            if (data.result == null) {
                draw += 1;
            } else if (data.result === 1) {
                win += 1;
            } else {
                loss += 1;
            }
        }
        counter += 1;
    });
    let result = win + "/" + draw + "/" + loss;
    if (lastYearResult !== result) {
        let chart = document.getElementById("chartYearId").getContext("2d");
        let total = win + draw + loss;
        if (chartYearId) {
            chartYearId.destroy()
        }
        chartYearId = new Chart(chart, {
            type: 'pie',
            data: {
                labels: ["win", "draw", "loss"],
                datasets: [{
                    data: [(win * 100 / total).toFixed(1), (draw * 100 / total).toFixed(1),
                    (loss * 100 / total).toFixed(1)],
                    backgroundColor: ['MediumSeaGreen', 'Orange', 'Tomato'],
                    hoverOffset: 5
                }],
            },
            options: {
                responsive: false,
                plugins: {
                    legend: {
                        display: true,
                        position: "bottom",
                        align: "center"
                    }
                }
            }
        });
        lastYearResult = result;
    }
    return result;
}

function formatterDate(value, row) {
    let date = new Date(value)
    let year = date.toLocaleString('default', {year: '2-digit'});
    let month = date.toLocaleString('default', {month: '2-digit'});
    let day = date.toLocaleString('default', {day: '2-digit'});
    return `${year}/${month}/${day}`;
}

function swapButton(){
    let submit = document.getElementById("submit");
    let spinner = document.getElementById("spinner");
    submit.style.display = "none";
    spinner.style.display = "block";
}