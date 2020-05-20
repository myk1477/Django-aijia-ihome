$(document).ready(function(){
    $.ajax({
        url: host + "/api/v1.0/user/auth",
        type: "get",
        xhrFields: {withCredentials: true},
        success: function (resp) {
            if (resp.errno == "0"){
                if (resp.data.real_name && resp.data.id_card) {
                // 如果用户已实名认证,那么就去请求之前发布的房源
                    $.ajax({
                        url: host + "/api/v1.0/user/houses",
                        type: "get",
                        xhrFields: {withCredentials: true},
                        success: function (resp) {
                            if (resp.errno == "0") {
                            $("#houses-list").html(template("houses-list-tmpl", {"houses": resp.data.houses}))
                        }
                        }
                    })

                }else {
                    $(".auth-warn").show();
                }

            }else if (resp.errno == "4101") {
                location.href = "/login.html"
            }
        }
    })
    $("#form-house-info").submit(function (e) {
        e.preventDefault();
        // 检验表单数据是否完整
        // 将表单的数据形成json，向后端发送请求
        var formData = {};
        $(this).serializeArray().map(function (x) { formData[x.name] = x.value });

        // 对于房屋设施的checkbox需要特殊处理
        var facility = [];
        $("input:checkbox:checked[name=facility]").each(function(i, x){ facility[i]=x.value });
        formData.facility = facility;

        // 使用ajax向后端发送请求
        $.ajax({
            url: host + "/api/v1.0/houses",
            type: "post",
            data: JSON.stringify(formData),
            contentType: "application/json",
            dataType: "json",
            xhrFields: {withCredentials: true},
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            success: function(resp){
                if ("4101" == resp.errno) {
                    location.href = "/login.html";
                } else if ("0" == resp.errno) {
                    // 后端保存数据成功
                    // 隐藏基本信息的表单
                    $("#form-house-info").hide();
                    // 显示上传图片的表单
                    $("#form-house-image").show();
                    // 设置图片表单对应的房屋编号那个隐藏字段
                    $("#house-id").val(resp.data.house_id);
                } else {
                    alert(resp.errmsg);
                }
            }
        });
    })
})
