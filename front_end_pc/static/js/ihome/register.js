function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function generateUUID() {
    var d = new Date().getTime();
    if(window.performance && typeof window.performance.now === "function"){
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid;
}
var imageCodeId = ""
var preImageCodeId = ""
// 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
function generateImageCode() {
    // 1. 生成验证码的编码
    imageCodeId = generateUUID()
    // 2. 设置验证码的标签的src
    var url = host + "/api/v1.0/imagecode?cur=" + imageCodeId + "&pre=" + preImageCodeId
    // 设置图片验证码的标签所对应的src
    $(".image-code>img").attr("src", url)
    preImageCodeId = imageCodeId
}

function sendSMSCode() {
    // 校验参数，保证输入框有数据填写
    $(".phonecode-a").removeAttr("onclick");
    var mobile = $("#mobile").val();
    if (!mobile) {
        $("#mobile-err span").html("请填写正确的手机号！");
        $("#mobile-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    } 
    var imageCode = $("#imagecode").val();
    if (!imageCode) {
        $("#image-code-err span").html("请填写验证码！");
        $("#image-code-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    }

    var params = {
        "mobile": mobile,
        "text": imageCode,
        "id": imageCodeId
    }

    // 通过ajax方式向后端接口发送请求，让后端发送短信验证码
    $.ajax({
        url: host + "/api/v1.0/sms",
        type: "post",
        contentType: "application/json",
        headers: {
            "X-CSRFToken": getCookie("csrf_token")
        },
        data: JSON.stringify(params),
        success: function (resp) {
            if (resp.errno == "0") {
                // 代表发送成功
                // 倒计时
                var num = 60
                var t = setInterval(function () {
                    if (num == 1) {
                        // 倒计时完成
                        clearInterval(t)
                        $(".phonecode-a").html("获取验证码")
                    }else {
                        num -= 1
                        // 更新按钮上的文字内容
                        $(".phonecode-a").html(num + "秒")
                    }
                }, 1000, 60)
            }else {
                alert(resp.errmsg)
                $(".phonecode-a").attr("onclick", "sendSMSCode();");
            }
        }
    })
}

$(document).ready(function() {
    generateImageCode();  // 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#imagecode").focus(function(){
        $("#image-code-err").hide();
    });
    $("#phonecode").focus(function(){
        $("#phone-code-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
        $("#password2-err").hide();
    });
    $("#password2").focus(function(){
        $("#password2-err").hide();
    });

    // 注册的提交(判断参数是否为空)
    
    $(".form-register").submit(function (e) {
        // 阻止默认提交事件
        e.preventDefault()

        // 实现自己的POST请求逻辑
        var mobile = $("#mobile").val()
        var phonecode = $("#phonecode").val()
        var password = $("#password").val()
        var password2 = $("#password2").val()

        if (!mobile) {
            // 弹出提示
            $("#mobile-err span").html("请输入手机号")
            $("#mobile-err").show();
            return
        }
        if (!phonecode) {
            $("#phone-code-err span").html("请填写短信验证码！");
            $("#phone-code-err").show();
            return;
        }
        if (!password) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }
        if (password != password2) {
            $("#password2-err span").html("两次密码不一致!");
            $("#password2-err").show();
            return;
        }

        var params = {
            "mobile": mobile,
            "phonecode": phonecode,
            "password": password
        }

        // 通过ajax方式向后端接口发送请求，让后端发送短信验证码
        $.ajax({
            url: host + "/api/v1.0/users",
            type: "post",
            contentType: "application/json",
            // 跨域
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
                    $("#password2-err span").html(resp.errmsg);
                    $("#password2-err").show();
                }
            }
        })
    })
})
