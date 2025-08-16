
// web/public/qr.js
// This script generates a QR code for a given URL and displays it in a div with the ID 'qrgenerator'.

function getQR(data){
    var div = document.getElementById('qrgenerator');
    while(div.firstChild){
        div.removeChild(div.firstChild);
    }

    let w = 77;
    if (data.length > 300){
        w = 128;
        data = data.substring(0, 300) + "...";
    }
    var qrcode = new QRCode("qrgenerator", {
        text: data,
        width: w,
        height: w,
        colorDark : "#000000",
        colorLight : "#ffffff",
        correctLevel : QRCode.CorrectLevel.H
    });
    var canvas = document.getElementById('qrgenerator').querySelector('canvas');

    var dataURL = canvas.toDataURL();
    console.log(dataURL);
    return canvas;
}
