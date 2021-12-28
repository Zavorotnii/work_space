async function testing() {
    document.getElementById("example-table").style.display = "none"
    document.getElementById("gif").style.display = "block"
    let dateReturn = document.getElementById("dateReturn").value;
    const rawResponse = await fetch('http://127.0.0.1:8080/returnVsd', {
        method: 'POST',
        headers: {
        },
        body: dateReturn
    });
    const serverData = await rawResponse.json();
    document.getElementById("gif").style.display = "none"
    document.getElementById("example-table").style.display = "block"
    showServerData(serverData, dateReturn);
}

function showServerData(serverData, dateReturn) {
    document.getElementById("example-table").style.display = "block"
    var tabledata = serverData;
    console.log(serverData);
    var table = new Tabulator("#example-table", {
        data: tabledata,
        pagination: "local",
        paginationSize: 15,
        printHeader: "<h2>Возвраты в меркурии за " + dateReturn + "</h2>",
        printRowRange: "selected",
        columns: [
            {
                formatter: "rowSelection", titleFormatter: "rowSelection", hozAlign: "center",
                headerSort: false, cellClick: function (e, cell) {
                    cell.getRow().toggleSelect();
                }, print: false
            },
            { title: "Код", field: "code_gp" },
            { title: "Название", field: "name" },
            { title: "Статус", field: "vetDStatus" },
            { title: "Вес", field: "volume" },
            { title: "GTIN", field: "gtin" },
            { title: "UUID", field: "uuid", print: false },
            { title: "Дата возврата", field: "dateReturn" },
            { title: "ТТН", field: "ttn", bottomCalc: "count", sorter: "number" },
            { title: "Статус2", field: "tick", hozAlign: "center", formatter: "tickCross" },
        ],
    });
    document.getElementById("download-xlsx").addEventListener("click", function () {
        table.download("xlsx", "Возвраты_" + dateReturn + ".xlsx", { sheetName: "Возвраты" });
    });
    document.getElementById("print-table").addEventListener("click", function () {
        table.print(false, true);
    });
}




//     const url = "http://127.0.0.1:8080/withdrawn";
// async function sendToServer() {
//     console.log('serverData')
//     let response = await fetch(url);
//     let serverData = await response.json();
//     showServerData(serverData);
// }

// function testpost() {
//     let start = document.getElementById("start").value;
//     $.ajax({

//         type: 'POST',
//         url: "http://127.0.0.1:8080/server",
//         data: start,
//         success: function (data) {
//             console.log(data)
//         },
//     });
// }

