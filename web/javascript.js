function cellStyleResult(value, row, index) {
    var result = 'draw';
    if (row.result != null) {
        result = row.result == 1 ? 'win' : 'lose';
    }
    return {
        classes: result
    }
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