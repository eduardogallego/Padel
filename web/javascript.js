var chartId;
var chart10Id;
var lastResult;
var last10Result;

function cellStylePartnerResult(value, row, index) {
    var result = '';
    var sum = row.pw - row.pl;
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
    var result = '';
    var sum = row.pw + row.rw - row.pl - row.rl;
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
    var result = '';
    var sum = row.pw + row.rw - row.pl - row.rl;
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
    var result = '';
    var sum = row.rw - row.rl;
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
    var result = 'draw';
    if (row.result != null) {
        result = row.result == 1 ? 'win' : 'loss';
    }
    return {
        classes: 'index ' + result
    }
}

function cellStyleMatchResult(value, row, index) {
    var result = 'draw';
    if (row.result != null) {
        result = row.result == 1 ? 'win' : 'loss';
    }
    return {
        classes: result
    }
}

function footItemCountFormatter(data) {
    return data.length;
}

function footResults(data) {
    var win = 0;
    var loss = 0
    var draw = 0;
    data.forEach(function(data) {
        if (data.result == null) {
            draw += 1;
        } else if (data.result == 1) {
            win += 1;
        } else {
            loss += 1;
        }
    });
    result = win + " / " + draw + " / " + loss;
    if (lastResult !== result) {
        var chart = document.getElementById("chartId").getContext("2d");
        var total = win + draw + loss;
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
        lastResult = result;
    }
    return result;
}

function foot10Results(data) {
    var win = 0;
    var loss = 0
    var draw = 0;
    var counter = 0;
    data.forEach(function(data) {
        if (counter < 10) {
            if (data.result == null) {
                draw += 1;
            } else if (data.result == 1) {
                win += 1;
            } else {
                loss += 1;
            }
        }
        counter += 1;
    });
    result = win + " / " + draw + " / " + loss;
    if (last10Result !== result) {
        var chart = document.getElementById("chart10Id").getContext("2d");
        var total = win + draw + loss;
        if (chart10Id) {
            chart10Id.destroy()
        }
        chart10Id = new Chart(chart, {
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
        last10Result = result;
    }
    return result;
}

function formatterDate(value, row) {
    var date = new Date(value)
    var year = date.toLocaleString('default', {year: '2-digit'});
    var month = date.toLocaleString('default', {month: '2-digit'});
    var day = date.toLocaleString('default', {day: '2-digit'});
    return `${year}/${month}/${day}`;
}

function swapButton(){
    var submit = document.getElementById("submit");
    var spinner = document.getElementById("spinner");
    submit.style.display = "none";
    spinner.style.display = "block";
}