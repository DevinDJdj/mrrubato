// Copyright 2023 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     https://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// Registering this listener when the script is first executed ensures that the
// offscreen document will be able to receive messages when the promise returned
// by `offscreen.createDocument()` resolves.

const header = document.querySelector('h1');

const generateDMS = (coords, isLat) => {
  const absCoords = Math.abs(coords);
  const deg = Math.floor(absCoords);
  const min = Math.floor((absCoords - deg) * 60);
  const sec = ((absCoords - deg - min / 60) * 3600).toFixed(1);
  const direction = coords >= 0 ? (isLat ? 'N' : 'E') : isLat ? 'S' : 'W';

  return `${deg}°${min}'${sec}"${direction}`;
};


function updateQRCode(text) {
    const div = document.getElementById('qrcode');
    while(div.firstChild){
        div.removeChild(div.firstChild);
    }

    var qrcode = new QRCode("qrcode", {
        text: text,
        width: 128,
        height: 128,
        colorDark : "#000000",
        colorLight : "#ffffff",
        correctLevel : QRCode.CorrectLevel.H
    });
//   div.innerHTML = "";
//   div.innerHTML = text;

}
chrome.tabs.query({'active': true, 'windowId': chrome.windows.WINDOW_ID_CURRENT},
  function(tabs){
    updateQRCode(tabs[0].url);
  }
);

navigator.geolocation.getCurrentPosition(
  (loc) => {
    const { coords } = loc;
    let { latitude, longitude } = coords;
    latitude = generateDMS(latitude, true);
    longitude = generateDMS(longitude);

    header.innerText = `position: ${latitude}, ${longitude}`;
  },
  (err) => {
    header.innerText = 'error (check console)';
    console.error(err);
  }
);
