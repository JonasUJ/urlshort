function is_valid_url(url) {
    return /^(http(s)?:\/\/)?(www\.)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$/.test(url);
}

function has_valid_chars(name) {
    return /^[\w\-]{0,9}$/.test(name);
}

function show_error(msg) {
    $("#error-text i").text(msg);
    $("#error-text").collapse("show");
}

function hide_error() {
    $("#error-text").collapse("hide");
}

function show_error_key(msg) {
    $("#error-text-key i").text(msg);
    $("#error-text-key").collapse("show");
}

function hide_error_key() {
    $("#error-text-key").collapse("hide");
}

function copyToClipboard(element) {
    var $temp = $("<input>");
    $temp.css("position", "fixed");
    $("body").prepend($temp);
    $temp.val($(element).text()).focus().select();
    document.execCommand("copy");
    $temp.remove();
}

$(document).ready(function () {
    $.ajaxSetup({
        headers: {
            "X-CSRFToken": $("input[name='csrfmiddlewaretoken']").val()
        }
    })

    let params = new URLSearchParams(window.location.search);
    if (params.has("urlname")) {
        $("#urlname").val(params.get("urlname"));
    }

    var keystore;
    var urlnamestore;
    $("#post-btn").click(() => {
        $("#post-btn").prop("disabled", true);
        hide_error_key();
        $("#picourl ~ .collapse").collapse("hide");
        $("#key-submit").removeClass("btn-success");
        $("#key").val("");
        $.post({
            url: "/api",
            data: {
                link: $("#link-input").val(),
                urlname: $("#urlname").val(),
            },
            success: (resp) => {
                switch (resp.error_code) {
                    case 0: // Success
                        hide_error();
                        $("#url-copy").removeClass("btn-success");
                        $("#url-modal #picourl").text(resp.short);
                        $("#url-modal").modal("show");
                        keystore = resp.key;
                        urlnamestore = resp.name;
                        break;
                    case 3:
                        show_error("Det navn er allerede taget");
                        break;
                    case 4:
                        show_error("URL er ikke valid");
                        break;
                    case 5:
                        show_error("Siden kunne ikke findes");
                        break;
                    case 6:
                        show_error("Navnet er ikke tilladt");
                        break;
                    case 7:
                        show_error("Link er ikke tilladt");
                        break;
                    case 1:
                    default:
                        show_error("Der skete en ukendt fejl");
                        break;
                }
                $("#urlname").trigger("input");
                $("#post-btn").prop("disabled", false);
            },
            error: (x, t, m) => {
                if (t == "timeout") {
                    show_error("Serveren var for langsom om at svare")
                } else {
                    show_error("Der skete en ukendt fejl")
                }
                $("#urlname").trigger("input");
                $("#post-btn").prop("disabled", false);
            },
            timeout: 8000
        }

        )
    });

    $("#url-copy").click(() => {
        copyToClipboard("#picourl")
        $("#url-copy").addClass("btn-success");
    });

    $("#key-btn").click(() => {
        $("#picourl ~ .collapse").collapse("toggle");
    });

    $("#key-submit").click(() => {
        $("#key-submit").removeClass("btn-success");
        $.post(
            "/api",
            {
                urlname: urlnamestore,
                key: keystore,
                newkey: $("#key").val(),
            },
            (resp) => {
                switch (resp.error_code) {
                    case 0:
                        hide_error_key();
                        keystore = resp.key;
                        $("#key-submit").addClass("btn-success");
                        break;
                    case 8:
                    case 10:
                        show_error_key("Nøglen kan ikke længere ændres");
                        break;
                    default:
                        show_error_key("Der skete en ukendt fejl");
                        break;
                }
            }
        )
    });

    $("#link-input").on("input", () => {
        if (is_valid_url($("#link-input").val())) {
            $("#link-input").removeClass("is-invalid");
        } else {
            $("#link-input").addClass("is-invalid");
        }
    });

    var xhr;
    $("#urlname-check").hide();
    $("#urlname-cross").show();
    $("#urlname-spinner").hide();
    $("#urlname").on("input", () => {
        if (xhr) { xhr.abort(); }
        $("#urlname").tooltip("disable");
        $("#urlname").tooltip("hide");
        if ($("#urlname").val() == "") {
            $("#urlname-check").hide();
            $("#urlname-cross").hide();
            $("#urlname-spinner").hide();
            return;
        }
        if (!has_valid_chars($("#urlname").val())) {
            $("#urlname").tooltip("enable");
            $("#urlname").tooltip("show");
            $("#urlname-check").hide();
            $("#urlname-cross").show();
            $("#urlname-spinner").hide();
            return;
        }
        $("#urlname-check").hide();
        $("#urlname-cross").hide();
        $("#urlname-spinner").show();
        xhr = $.get(
            "/api",
            { urlname: $("#urlname").val() },
            (resp) => {
                if (resp.error_code == 2) {
                    $("#urlname-check").show();
                } else {

                    $("#urlname-cross").show();
                }
                $("#urlname-spinner").hide();
            }
        )
    });
    $("#urlname").trigger("input");
});

