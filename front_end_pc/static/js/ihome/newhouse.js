function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    // $('.popup_con').fadeIn('fast');
    // $('.popup_con').fadeOut('fast');

    // 在页面加载完毕之后获取区域信息
    $.ajax({
        url: host + "/api/v1.0/areas",
        type: "get",
        xhrFields: {withCredentials: true},
        success: function (resp) {
            if (resp.errno == "0") {
            // 取出数据，遍历添加选项
            // for(var i=0;i<resp.data.areas.length;i++){
            //     var areaId = resp.data.areas[i].aid
            //     var areaName = resp.data.areas[i].aname
            //     // 将选项添加到 select 中
            //     $("#area-id").append('<option value="'+ areaId +'">' + areaName + '</option>')
            // }
            // render_template("index.html", data=data)
            var html = template("areas-tmpl", {"areas": resp.data})
            $("#area-id").html(html)
        }
        }
    })

    // 处理房屋基本信息提交的表单数据
    $("#form-house-info").submit(function (e) {
        e.preventDefault()


        // 拼接参数
        var params = {}
        $(this).serializeArray().map(function (x) {
            params[x.name] = x.value
        })


        var facilities = []
        // 处理设施信息
        $(":checkbox:checked[name=facility]").each(function (i, x) {
            facilities[i] = x.value
        })
        params["facility"] = facilities

        $.ajax({
            url: host + "/api/v1.0/houses",
            type: "post",
            contentType: "application/json",
            data: JSON.stringify(params),
            headers: {
                "X-CSRFToken": getCookie("csrf_token"),
            },
            xhrFields: {withCredentials: true},
            success: function (resp) {
                if (resp.errno == "0") {
                    // 显示上传图片的界面
                    $("#form-house-info").hide()
                    $("#form-house-image").show()
                    $("#house-id").val(resp.data.house_id)
                }else {
                    alert(resp.errmsg)
                }
            }
        })
    })

    // // TODO: 处理图片表单的数据
    // $("#form-house-info").hide()
    // $("#form-house-image").show()
    // $("#house-id").val('2')

    $("#form-house-image").submit(function (e) {
        e.preventDefault()

        var house_id = $("#house-id").val()

        $(this).ajaxSubmit({
            url: host + "/api/v1.0/houses/" + house_id + "/images",
            type: "post",
            xhrFields: {withCredentials: true},
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            success: function (resp) {
                if (resp.errno == "0") {
                    $(".house-image-cons").append('<img src="' + resp.data.url + '">')
                } else if (resp.errno == "4101") {
                    location.href = "/login.html"
                }
            }
        })
    })
})