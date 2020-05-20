function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function() {
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
    });
    // 添加登录表单提交操作
    $(".form-login").submit(function(e){
        e.preventDefault();
        mobile = $("#mobile").val();
        password = $("#password").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        } 
        if (!password) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }

        // var params = {
        //     "mobile": mobile,
        //     "password": password
        // }
        // 拼接参数的方式
        var params = {}
        $(".form-login").serializeArray().map(function (x) {
            params[x.name] = x.value
        })
        // 通过ajax方式向后端接口发送请求，让后端发送短信验证码
        $.ajax({
            url: host + "/api/v1.0/session",
            type: "post",
            contentType: "application/json",
            xhrFields: {
                withCredentials: true
            },
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            data: JSON.stringify(params),
            success: function (resp) {
                if (resp.errno == "0") {
                    // 跳转到首页
                    location.href = "/index.html"
                }else {
                    $(".error-msg span").html(resp.errmsg);
                    $(".error-msg").show();
                }
            }
        })

    });
})
