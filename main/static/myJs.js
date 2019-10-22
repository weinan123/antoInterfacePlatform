//公共提示框

window.alert = function (txt, time) {
    if (document.getElementById("alertFram")) {
        return;
    }
    // 遮罩层
    var shield = document.createElement("DIV");
    shield.className = "shieldClass";
    shield.id = "shield";
    shield.style.position = "absolute";
    shield.style.left = "0px";
    shield.style.top = "0px";
    shield.style.width = "100%";
    shield.style.height = "100%";
    //弹出对话框时的背景颜色
    shield.style.background = "#111";
    shield.style.textAlign = "center";
    shield.style.zIndex = "25000";
    shield.style.opacity = "0.4";
    var alertDiv = document.createElement("DIV");
    alertDiv.id = "alertFram";
    alertDiv.style.position = "absolute";
    alertDiv.style.left = "50%";
    alertDiv.style.top = "40%";
    alertDiv.style.marginLeft = "-225px";
    alertDiv.style.marginTop = "-75px";
    alertDiv.style.width = "450px";
    alertDiv.style.height = "150px";
    alertDiv.style.background = "#ccc";
    alertDiv.style.textAlign = "center";
    alertDiv.style.lineHeight = "150px";
    alertDiv.style.zIndex = "10000";
    alertDiv.style.zIndex = "9999999";
    alertDiv.innerHTML = "<ul style='list-style:none;margin:0px;padding:0px;width:100%'><li style='background:#2372A8;text-align:left;padding-left:10px;font-size:16px;font-weight:bold;height:27px;line-height:25px;border:1px solid #2372A8;color:white'>提示:</li><li style='background:#fff;text-align:center;font-size:16px;height:120px;line-height:120px;border-left:1px solid #2372A8;border-right:1px solid #2372A8;'>" + txt + "</li><li style='background:#2372A8;text-align:center;font-weight:bold;height:27px;line-height:25px; border:1px solid #2372A8;'onclick='doOk()'><input type='button' style='background-color: #2372A8;padding-top: 0px;border: none;outline:none;color:white' value='确 定'/></li></ul>";
    document.body.appendChild(alertDiv);
     document.body.appendChild(shield);
    var c = 0;
    this.timer = function () {
        if (c++ >= time) {
            clearInterval(ad);
            document.body.removeChild(alertDiv);
            document.body.removeChild(shield);
        }
    };
    var ad = setInterval("timer()", 1000);
    this.doOk = function () {
        document.body.removeChild(alertDiv);
        document.body.removeChild(shield);
    };
    alertDiv.focus();
    document.body.onselectstart = function () {
        return false;
    };
};
zdconfirm = function(txt,callback){
    myzconfirm(txt,function (result) {
        if( callback ) callback(result)
    })
};
myzconfirm = function (txt,callback) {
    if (document.getElementById("alertFram")) {
        return;
    }
    // 遮罩层
    var shield = document.createElement("DIV");
    shield.className = "shieldClass";
    shield.id = "shield";
    shield.style.position = "absolute";
    shield.style.left = "0px";
    shield.style.top = "0px";
    shield.style.width = "100%";
    shield.style.height = "100%";
    //弹出对话框时的背景颜色
    shield.style.background = "#111";
    shield.style.textAlign = "center";
    shield.style.zIndex = "25000";
    shield.style.opacity = "0.4";
    var alertDiv = document.createElement("DIV");
    alertDiv.id = "alertFram";
    alertDiv.style.position = "absolute";
    alertDiv.style.left = "50%";
    alertDiv.style.top = "40%";
    alertDiv.style.marginLeft = "-225px";
    alertDiv.style.marginTop = "-75px";
    alertDiv.style.width = "450px";
    alertDiv.style.height = "150px";
    alertDiv.style.background = "#ccc";
    alertDiv.style.textAlign = "center";
    alertDiv.style.lineHeight = "150px";
    alertDiv.style.zIndex = "10000";
    alertDiv.style.zIndex = "9999999";
    alertDiv.innerHTML = "<ul style='list-style:none;margin:0px;padding:0px;width:100%'><li style='background:#2372A8;text-align:left;padding-left:10px;font-size:16px;font-weight:bold;height:27px;line-height:25px;border:1px solid #2372A8;color:white'>提示:</li><li style='background:#fff;text-align:center;font-size:16px;height:120px;line-height:120px;border-left:1px solid #2372A8;border-right:1px solid #2372A8;'>" + txt + "</li><li style='text-align:center;font-weight:bold;height:27px;line-height:25px; '>" +
        "<input onclick='doOk()' type='button' style='float:left;width:50%;background-color: #ccc;padding-top: 0px;border: none;outline:none;color:#2372A8' value='取 消'/>" +
        "<input onclick='doconfirm()' type='button' style='float:left;width:50%;background-color: #2372A8;padding-top: 0px;border: none;outline:none;color:white' value='确 定'/></li></ul>";
    document.body.appendChild(alertDiv);
    document.body.appendChild(shield);
    this.doOk = function () {
        if( callback ) callback(false);
        document.body.removeChild(alertDiv);
        document.body.removeChild(shield);

    };
    this.doconfirm=function(){
        if( callback ) callback(true);
         document.body.removeChild(alertDiv);
        document.body.removeChild(shield);

    };
    alertDiv.focus();
    document.body.onselectstart = function () {
        return false;
    };
};


