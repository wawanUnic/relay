function setRelay(relay, status) {
    var url = status ? 'on/' : 'off/';
    callApiWithRelay(url, relay);
}

function toggleRelay(relay) {
    callApiWithRelay('toggle/', relay);
}

function callApiWithRelay(url, relay) {
    url += relay;
    callApi(url);
}

function callApi(url) {
    $.get(url, function () {
    }).done(function () {
    }).fail(function () {
        swal({
            title: "Pi-контроллер",
            text: "Ошибка сервера",
            type: "error"
        });
    });
}
