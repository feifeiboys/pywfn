var Width=document.body.clientWidth
var Height=document.body.clientHeight
var msgBox=document.getElementById('control')
var msgBut=document.getElementById('show_btn')
msgBut.onclick=(event)=>{
    if(showMsg){
        showMsg=false;
        msgBox.style.left=`${Width}px`
        msgBut.style.left=`${Width-buttonSize}px`
    }else{
        showMsg=true;
        msgBox.style.left=`${Width*(1-msgBoxRatio)}px`
        msgBut.style.left=`${Width*(1-msgBoxRatio)-buttonSize}px`
    }
}

var showMsg=true
var buttonSize=40
var msgBoxRatio=0.2
msgBut.style.left=`${Width*(1-msgBoxRatio)-buttonSize}px`
msgBut.style.width=`${buttonSize}px`
msgBut.style.height=`${buttonSize}px`

msgBox.style.width=`${Width*msgBoxRatio}px`
msgBox.style.left=`${Width*(1-msgBoxRatio)}px`
