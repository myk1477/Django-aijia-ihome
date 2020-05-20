//模态框居中的控制
function centerModals(){
    $('.modal').each(function(i){   //遍历每一个模态框
        var $clone = $(this).clone().css('display', 'block').appendTo('body');    
        var top = Math.round(($clone.height() - $clone.find('.modal-content').height()) / 2);
        top = top > 0 ? top : 0;
        $clone.remove();
        $(this).find('.modal-content').css("margin-top", top-30);  //修正原先已经有的30个像素
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    $('.modal').on('show.bs.modal', centerModals);      //当模态框出现的时候
    $(window).on('resize', centerModals);
    // 查询房东的订单
    $.ajax({
        url: host + "/api/v1.0/orders?role=landlord",
        type: "get",
        xhrFields: {withCredentials: true},
        success: function (resp) {
            if ("0" == resp.errno) {
            $(".orders-list").html(template("orders-list-tmpl", {orders:resp.data.orders}));
            // 点击列表页接单按钮的时候,将订单id设置到弹框的确认键上
            $(".order-accept").on("click", function(){
                // 获取订单id
                var orderId = $(this).parents("li").attr("order-id");
                // 设置到弹框的确认键上,以及后续获取
                $(".modal-accept").attr("order-id", orderId);
            });
            // 接单处理
            $(".modal-accept").on("click", function(){
                // 获取订单id
                var orderId = $(this).attr("order-id");
                $.ajax({
                    url: host + "/api/v1.0/orders/"+orderId+"/status",
                    type:"PUT",
                    data:'{"action":"accept"}',
                    contentType:"application/json",
                    dataType:"json",
                    xhrFields: {withCredentials: true},
                    headers:{
                        "X-CSRFTOKEN":getCookie("csrf_token"),
                    },
                    success:function (resp) {
                        if ("4101" == resp.errno) {
                            location.href = "/login.html";
                        } else if ("0" == resp.errno) {
                            // 1. 设置订单状态的html
                            $(".orders-list>li[order-id="+ orderId +"]>div.order-content>div.order-text>ul li:eq(4)>span").html("已接单");
                            // 2. 隐藏接单和拒单操作
                            $("ul.orders-list>li[order-id="+ orderId +"]>div.order-title>div.order-operate").hide();
                            // 3. 隐藏弹出的框
                            $("#accept-modal").modal("hide");
                        }
                    }
                })
            });

            // 点击列表页接单按钮的时候,将订单id设置到弹框的确认键上
            $(".order-reject").on("click", function(){
                // 获取订单id
                var orderId = $(this).parents("li").attr("order-id");
                // 设置到弹框的确认键上,以及后续获取
                $(".modal-reject").attr("order-id", orderId);
            });
            // 处理拒单
            $(".modal-reject").on("click", function(){
                // 获取订单id
                var orderId = $(this).attr("order-id");
                var reject_reason = $("#reject-reason").val();
                // 如果没有填写拒单原因,直接返回
                if (!reject_reason) return;
                var data = {
                    action: "reject",
                    reason:reject_reason
                };
                $.ajax({
                    url: host + "/api/v1.0/orders/"+orderId+"/status",
                    type:"PUT",
                    data:JSON.stringify(data),
                    contentType:"application/json",
                    headers: {
                        "X-CSRFTOKEN":getCookie("csrf_token")
                    },
                    xhrFields: {withCredentials: true},
                    dataType:"json",
                    success:function (resp) {
                        if ("4101" == resp.errno) {
                            location.href = "/login.html";
                        } else if ("0" == resp.errno) {
                            // 1. 设置订单状态的html
                            $(".orders-list>li[order-id="+ orderId +"]>div.order-content>div.order-text>ul li:eq(4)>span").html("已拒单");
                            // 2. 隐藏接单和拒单操作
                            $("ul.orders-list>li[order-id="+ orderId +"]>div.order-title>div.order-operate").hide();
                            // 3. 隐藏弹出的框
                            $("#reject-modal").modal("hide");
                        }
                    }
                });
            })
        }
        }
    })

});