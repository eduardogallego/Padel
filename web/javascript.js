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
    return win + " / " + lose + " / " + draw;
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