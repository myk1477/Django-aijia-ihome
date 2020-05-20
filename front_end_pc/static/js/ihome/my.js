function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

// 点击推出按钮时执行的函数
function logout() {
    $.ajax({
        url: host + "/api/v1.0/session",
        type: "delete",
        xhrFields: {withCredentials: true},
        headers: {
            "X-CSRFToken": getCookie("csrf_token")
        },
        success: function (resp) {
            location.href = "/index.html"
        }
    })
}

$(document).ready(function(){

    $.ajax({
        url: host + "/api/v1.0/user",
        type: "get",
        xhrFields: {withCredentials: true},
        success: function (resp) {
            if (resp.errno == "0"){
                $("#user-avatar").attr("src", resp.data.avatar_url)
                $("#user-name").html(resp.data.name)
                $("#user-mobile").html(resp.data.mobile)
            }else if (resp.errno == "4101"){
                // 到登录页面去
                location.href = "/login.html"
            }
        }
    })

});
