
// web/public/qr.js
// This script generates a QR code for a given URL and displays it in a div with the ID 'qrgenerator'.

function getQR(data){
    var div = document.getElementById('qrscreen');

    let w = 77;
    if (data.length > 300){
        w = 128;
        data = data.substring(0, 900) + "...";
    }
    var qrcode = new QRCode("qrscreen", {
        text: data,
        width: w,
        height: w,
        colorDark : "#000000",
        colorLight : "#ffffff",
        correctLevel : QRCode.CorrectLevel.H
    });
    var canvas = document.getElementById('qrscreen').querySelector('canvas');

    var dataURL = canvas.toDataURL();
    console.log(dataURL);
    return canvas;
}
