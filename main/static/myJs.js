//公共提示框
window.alert = function(str) {
    if(document.querySelectorAll("div.shieldClass").length!=0){
    return false;
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
    //背景透明 IE有效
    var alertFram = document.createElement("DIV");
    alertFram.className = "alertFramClass";
    alertFram.id = "alertFram";
    alertFram.style.position = "absolute";
    alertFram.style.left = "50%";
    alertFram.style.top = "40%";
    alertFram.style.background = "rgba(0,0,0,0.7)";
    alertFram.style.textAlign = "center";
    alertFram.style.zIndex = "25001";
    alertFram.style.borderRadius="6px";
    strHtml = "<p style='text-align:center;padding:15px 15px;font-size:12px;font-weight: normal;color:#fff'>" + str +"</p>"
    alertFram.innerHTML = strHtml;
    document.body.appendChild(alertFram);
    document.body.appendChild(shield);
    var o = document.getElementById("alertFram");
    var body=document.getElementsByTagName("body")[0];
    var w = o.offsetWidth; //宽度
    o.style.marginLeft="-"+w/2+"px";
    setTimeout(function(){
        var shieldDom=document.querySelectorAll("div.shieldClass");
        var alertFramDom=document.querySelectorAll("div.alertFramClass");
        for(var i=0;i<shieldDom.length;i++){
        body.removeChild(shieldDom[i]);
        };
        for(var j=0;j<alertFramDom.length;j++){
        body.removeChild(alertFramDom[j]);
        };
    },2000);
};
//js加载等待动效
myonloading = function (str,status) {
    if(document.querySelectorAll("div.shieldClass").length!=0){
return false;
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
//背景透明 IE有效
var alertFram = document.createElement("DIV");
alertFram.className = "alertFramClass";
alertFram.id = "alertFram";
alertFram.style.position = "absolute";
alertFram.style.left = "50%";
alertFram.style.top = "40%";
alertFram.style.background = "rgba(0,0,0,0.7)";
alertFram.style.textAlign = "center";
alertFram.style.zIndex = "25001";
alertFram.style.borderRadius="6px";
strHtml = "<p style='text-align:center;padding:15px 15px;font-size:12px;font-weight: normal;color:#fff'>" + str +"</p>"
alertFram.innerHTML = strHtml;
document.body.appendChild(alertFram);
document.body.appendChild(shield);
var o = document.getElementById("alertFram");
var body=document.getElementsByTagName("body")[0];
var w = o.offsetWidth; //宽度
o.style.marginLeft="-"+w/2+"px";
if(status == 200){
    setTimeout(function(){
var shieldDom=document.querySelectorAll("div.shieldClass");
var alertFramDom=document.querySelectorAll("div.alertFramClass");
for(var i=0;i<shieldDom.length;i++){
body.removeChild(shieldDom[i]);
};
for(var j=0;j<alertFramDom.length;j++){
body.removeChild(alertFramDom[j]);
};
},2000);
}
};
