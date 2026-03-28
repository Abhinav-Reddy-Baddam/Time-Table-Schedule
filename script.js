let fromSelct = document.querySelector(".from_selct");
let toSelct = document.querySelector(".to_selct");
let fromImg = document.querySelector(".from_img");
let toImg = document.querySelector(".to_img");

fromSelct.addEventListener("change", function(){
    let value=fromSelct.value;
    if(value === "IND"){
        fromImg.src="https://flagsapi.com/IN/flat/64.png";
    }else if(value === "USA"){
        fromImg.src="https://flagsapi.com/US/flat/64.png";
    }else if(value === "AU"){
        fromImg.src="https://flagsapi.com/AU/flat/64.png";
    }else if(value === "GB"){
        fromImg.src="https://flagsapi.com/GB/flat/64.png";
    }
});
toSelct.addEventListener("change",function(){
    let value=toSelct.value;
    if(value === "IND"){
        toImg.src="https://flagsapi.com/IN/flat/64.png";
    }else if(value === "USA"){
        toImg.src="https://flagsapi.com/US/flat/64.png";
    }else if(value === "AU"){
        toImg.src="https://flagsapi.com/AU/flat/64.png";
    }else if(value === "GB"){
        toImg.src="https://flagsapi.com/GB/flat/64.png";
    }
})
