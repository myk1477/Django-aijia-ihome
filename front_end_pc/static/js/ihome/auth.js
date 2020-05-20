function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}


function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    // 查询用户的实名认证信息

    $.ajax({
        url: host + "/api/v1.0/user/auth",
        type: "get",
        xhrFields: {withCredentials: true},
        success: function (resp) {
            if (resp.errno == "0"){
                    // 判断是否有认证信息，如果有进行显示并且将保存按钮隐藏和输入框置为不可用
                if (resp.data.real_name && resp.data.id_card) {
                    // 进行显示
                    $("#real-name").val(resp.data.real_name)
                    $("#id-card").val(resp.data.id_card)
                    // 并且将保存按钮隐藏和输入框置为不可用
                    $(".btn-success").hide()
                    $("#real-name").prop("disabled", true)
                    $("#id-card").prop("disabled", true)
                }
            }else if (resp.errno == "4101"){
                location.href = "/login.html"
            }else {
            alert(resp.errmsg)
            }
        }
    })


    // 管理实名信息表单的提交行为
    $("#form-auth").submit(function (e) {
        e.preventDefault()


        var real_name = $("#real-name").val()
        var id_card = $("#id-card").val()

        if (!(real_name && id_card)) {
            $(".error-msg").show()
            return
        }

        $(".error-msg").hide()

        var params = {
            "real_name": real_name,
            "id_card": id_card,
        }


        $.ajax({
            url: host + "/api/v1.0/user/auth",
            type: "post",
            contentType: "application/json",
            data: JSON.stringify(params),
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            xhrFields: {withCredentials: true},
            success: function (resp) {
                if (resp.errno == "0") {
                    showSuccessMsg()
                    // 进行显示
                    $("#real-name").val(resp.data.real_name)
                    $("#id-card").val(resp.data.id_card)
                    // 并且将保存按钮隐藏和输入框置为不可用
                    $(".btn-success").hide()
                    $("#real-name").prop("disabled", true)
                    $("#id-card").prop("disabled", true)
                }else if (resp.errno == "4101") {
                    location.href = "/login.html"
                }else {
                    alert(resp.errmsg)
                }
            }
        })
    })
})