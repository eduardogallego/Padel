var chartId;

function cellStyleResult(value, row, index) {
    var result = 'draw';
    if (row.result != null) {
        result = row.result == 1 ? 'win' : 'lose';
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
    var lose = 0
    var draw = 0;
    data.forEach(function(data) {
        if (data.result == null) {
            draw += 1;
        } else if (data.result == 1) {
            win += 1;
        } else {
            lose += 1;
        }
    });
    var chart = document.getElementById("chartId").getContext("2d");
    if (chartId) {
        chartId.destroy()
    }
    chartId = new Chart(chart, {
        type: 'pie',
        data: {
            labels: ["win", "draw", "lose"],
            datasets: [{
                data: [win, draw, lose],
                backgroundColor: ['green', 'orange', 'red'],
                hoverOffset: 5
            }],
        },
        options: {
            responsive: false
        }
    });
    return win + " / " + draw + " / " + lose;
}

function formatterDate(value, row) {
    var date = new Date(value)
    return date.getDate() + "-" + (date.getMonth() + 1);
}

function swapButton(){
    var submit = document.getElementById("submit");
    var spinner = document.getElementById("spinner");
    submit.style.display = "none";
    spinner.style.display = "block";
}