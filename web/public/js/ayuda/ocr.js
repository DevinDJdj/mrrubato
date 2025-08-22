    const desiredWidth = 1000;
    const dropzone = document.getElementById('drop_zone');
    const fileInput = document.getElementById('fileInput');
    const imageContainer = document.querySelector('.image-container');
    const fullDocumentTextarea = document.getElementById('fullDocument');
    const fullDocumentSection = document.getElementById('fullDocumentSection');
    const languageSelect = document.getElementById('id_language');

    let fileSelectionAllowed = true;

    const LANGUAGES = {
      "afr": "Afrikaans",
      "amh": "Amharic",
      "ara": "Arabic",
      "asm": "Assamese",
      "aze": "Azerbaijani",
      "aze_cyrl": "Azerbaijani - Cyrillic",
      "bel": "Belarusian",
      "ben": "Bengali",
      "bod": "Tibetan",
      "bos": "Bosnian",
      "bul": "Bulgarian",
      "cat": "Catalan; Valencian",
      "ceb": "Cebuano",
      "ces": "Czech",
      "chi_sim": "Chinese - Simplified",
      "chi_tra": "Chinese - Traditional",
      "chr": "Cherokee",
      "cym": "Welsh",
      "dan": "Danish",
      "deu": "German",
      "dzo": "Dzongkha",
      "ell": "Greek, Modern (1453-)",
      "eng": "English",
      "enm": "English, Middle (1100-1500)",
      "epo": "Esperanto",
      "est": "Estonian",
      "eus": "Basque",
      "fas": "Persian",
      "fin": "Finnish",
      "fra": "French",
      "frk": "German Fraktur",
      "frm": "French, Middle (ca. 1400-1600)",
      "gle": "Irish",
      "glg": "Galician",
      "grc": "Greek, Ancient (-1453)",
      "guj": "Gujarati",
      "hat": "Haitian; Haitian Creole",
      "heb": "Hebrew",
      "hin": "Hindi",
      "hrv": "Croatian",
      "hun": "Hungarian",
      "iku": "Inuktitut",
      "ind": "Indonesian",
      "isl": "Icelandic",
      "ita": "Italian",
      "ita_old": "Italian - Old",
      "jav": "Javanese",
      "jpn": "Japanese",
      "kan": "Kannada",
      "kat": "Georgian",
      "kat_old": "Georgian - Old",
      "kaz": "Kazakh",
      "khm": "Central Khmer",
      "kir": "Kirghiz; Kyrgyz",
      "kor": "Korean",
      "kur": "Kurdish",
      "lao": "Lao",
      "lat": "Latin",
      "lav": "Latvian",
      "lit": "Lithuanian",
      "mal": "Malayalam",
      "mar": "Marathi",
      "mkd": "Macedonian",
      "mlt": "Maltese",
      "msa": "Malay",
      "mya": "Burmese",
      "nep": "Nepali",
      "nld": "Dutch; Flemish",
      "nor": "Norwegian",
      "ori": "Oriya",
      "pan": "Panjabi; Punjabi",
      "pol": "Polish",
      "por": "Portuguese",
      "pus": "Pushto; Pashto",
      "ron": "Romanian; Moldavian; Moldovan",
      "rus": "Russian",
      "san": "Sanskrit",
      "sin": "Sinhala; Sinhalese",
      "slk": "Slovak",
      "slv": "Slovenian",
      "spa": "Spanish; Castilian",
      "spa_old": "Spanish; Castilian - Old",
      "sqi": "Albanian",
      "srp": "Serbian",
      "srp_latn": "Serbian - Latin",
      "swa": "Swahili",
      "swe": "Swedish",
      "syr": "Syriac",
      "tam": "Tamil",
      "tel": "Telugu",
      "tgk": "Tajik",
      "tgl": "Tagalog",
      "tha": "Thai",
      "tir": "Tigrinya",
      "tur": "Turkish",
      "uig": "Uighur; Uyghur",
      "ukr": "Ukrainian",
      "urd": "Urdu",
      "uzb": "Uzbek",
      "uzb_cyrl": "Uzbek - Cyrillic",
      "vie": "Vietnamese",
      "yid": "Yiddish"
    }

    // Populate the languages select box
    while (languageSelect.firstChild) {
      languageSelect.removeChild(languageSelect.firstChild);
    }

    for (const code of Object.values(Tesseract.languages)) {
      const name = LANGUAGES[code];
      const option = document.createElement('option');
      option.value = code;
      option.textContent = name;
      if (option.value == 'eng') {
        option.selected = true;
      }
      languageSelect.appendChild(option);
    }

    function showFullDocument() {
      // Only shows if there are multiple populated textareas
      const populatedTextareas = Array.from(
        document.querySelectorAll('.image-container textarea')
      ).filter(ta => ta.value.trim().length);
      if (populatedTextareas.length > 1) {
        fullDocumentTextarea.value = populatedTextareas.map(ta => ta.value.trim()).join("\n\n");
        fullDocumentSection.style.display = 'block';
      } else {
        fullDocumentTextarea.value = '';
        fullDocumentSection.style.display = 'none';
      }
    }

    function setTextarea(ta, text) {
      ta.value = text.trim();
      // Set textarea height to fit content
      ta.style.height = 'auto';
      ta.style.height = (ta.scrollHeight + 5) + 'px';
    }

//    dropzone.addEventListener('dragover', handleDragOver);
//    dropzone.addEventListener('dragleave', handleDragLeave);
//    dropzone.addEventListener('drop', handleDrop);
//    dropzone.addEventListener('click', handleClick);

    async function handleDragOver(event) {
      event.preventDefault();
      if (fileSelectionAllowed) {
        dropzone.classList.add('drag-over');
      }
    }

    async function handleDragLeave(event) {
      event.preventDefault();
      if (fileSelectionAllowed) {
        dropzone.classList.remove('drag-over');
      }
    }

    async function handleDrop(event) {
      event.preventDefault();
      if (fileSelectionAllowed) {
        dropzone.classList.remove('drag-over');
        const file = event.dataTransfer.files[0];
        fileInput.files = event.dataTransfer.files;
        processFileOCR(file);
      }
    }

    async function handleClick() {
      if (fileSelectionAllowed) {
        fileInput.click();
      }
    }

    fileInput.addEventListener('change', (event) => {
      const file = event.target.files[0];
      processFileOCR(file);
    });

    async function processImage(imageURL){
      const worker = await Tesseract.createWorker(languageSelect.value);
//      const ta = await displayImage(imageURL);
      const ta = await displayTextArea(imageURL);
      const { text } = await ocrImage(worker, imageURL);
      setTextarea(ta, text);
//      showFullDocument();

      await worker.terminate();
      return text;

    }

    async function processFileOCR(file) {
      const worker = await Tesseract.createWorker(languageSelect.value);
      fullDocumentTextarea.value = '';
      fullDocumentSection.style.display = 'none';
      imageContainer.innerHTML = '';
      const originalText = dropzone.innerText;
      dropzone.innerText = 'Processing file...';
      dropzone.classList.add('disabled');
      fileSelectionAllowed = false;
      let ret = "";
      if (file.type === 'application/pdf') {
        const { numPages, imageIterator } = await convertPDFToImages(file);
        let done = 0;
        dropzone.innerText = `Processing ${numPages} page${numPages > 1 ? 's' : ''}`;
        for await (const { imageURL } of imageIterator) {
          const ta = await displayImage(imageURL);
          const { text } = await ocrImage(worker, imageURL);
          ret += text + "\n\n";
          setTextarea(ta, text);
          showFullDocument();
          done += 1;
          dropzone.innerText = `Done ${done} of ${numPages}`;
        }
      } else {
        const imageURL = URL.createObjectURL(file);
        const ta = await displayImage(imageURL);
        const { text } = await ocrImage(worker, imageURL);
        setTextarea(ta, text);
        ret = text;
        showFullDocument();
      }

      await worker.terminate();
      dropzone.innerText = originalText;
      dropzone.classList.remove('disabled');
      fileSelectionAllowed = true;
      return ret;
    }

    async function displayTextArea(imageURL){
      const altTextarea = document.getElementById("ocr-processing");
      altTextarea.classList.add('textarea-alt');
      altTextarea.placeholder = 'OCRing image...';
      imageContainer.appendChild(altTextarea);

      return altTextarea;
    }

    async function displayImage(imageURL) {
      const imgElement = document.createElement('img');
      imgElement.src = imageURL;
      imageContainer.appendChild(imgElement);

      const altTextarea = document.createElement('textarea');
      altTextarea.classList.add('textarea-alt');
      altTextarea.placeholder = 'OCRing image...';
      imageContainer.appendChild(altTextarea);

      return altTextarea;
    }

    async function rerunOCR() {
      const textareas = document.querySelectorAll('.image-container textarea');
      const images = document.querySelectorAll('.image-container img');

      if (!textareas.length) {
        return;
      }

      // Blank all the textareas
      Array.from(textareas).forEach(ta => ta.value = '');
      showFullDocument();

      const numImages = images.length;
      let done = 0;
      dropzone.innerText = `Processing ${numImages} image${numImages > 1 ? 's' : ''}`;

      const worker = await Tesseract.createWorker(languageSelect.value);

      for (let i = 0; i < numImages; i++) {
        const imageURL = images[i].src;
        const ta = textareas[i];
        ta.placeholder = 'OCRing image...';
        const { text } = await ocrImage(worker, imageURL);
        setTextarea(ta, text);
        showFullDocument();
        done += 1;
        dropzone.innerText = `Done ${done} of ${numImages}`;
      }
      await worker.terminate();
    }


    document.addEventListener('paste', (event) => {
      const items = (event.clipboardData || event.originalEvent.clipboardData).items;
      const images = Array.from(items).filter(item => item.type.indexOf('image') !== -1);
      if (images.length) {
        processFileOCR(images[0].getAsFile());
      }
    });

    async function convertPDFToImages(file) {
      // returns { numPages, imageIterator }
      const pdf = await pdfjsLib.getDocument(URL.createObjectURL(file)).promise;
      const numPages = pdf.numPages;
      async function* images() {
        for (let i = 1; i <= numPages; i++) {
          try {
            const page = await pdf.getPage(i);
            const viewport = page.getViewport({ scale: 1 });
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            canvas.width = desiredWidth;
            canvas.height = (desiredWidth / viewport.width) * viewport.height;
            const renderContext = {
              canvasContext: context,
              viewport: page.getViewport({ scale: desiredWidth / viewport.width }),
            };
            await page.render(renderContext).promise;
            const imageURL = canvas.toDataURL('image/jpeg', 0.8);
            yield { imageURL };
          } catch (error) {
            console.error(`Error rendering page ${i}:`, error);
          }
        }
      }
      return { numPages: numPages, imageIterator: images() };
    }

    async function ocrImage(worker, imageUrl) {
      const {
        data: { text },
      } = await worker.recognize(imageUrl);
      return { text };
    }

    // Update URL bar to match language select
    languageSelect.addEventListener('change', async (event) => {
      let newUrl = window.location.pathname;
      let language = event.target.value;
      if (language != 'eng') {
        newUrl += '?language=' + language;
      }
      window.history.pushState({ path: newUrl }, '', newUrl);
      await rerunOCR();
    });

    function setLanguageFromQueryString() {
      const params = new URLSearchParams(window.location.search);
      let value = params.get('language');
      if (!value) {
        value = 'eng';
      }
      languageSelect.value = value;
    }

    // Set the select box value when the page loads
    window.addEventListener('load', setLanguageFromQueryString);

    window.addEventListener('popstate', (event) => {
      setLanguageFromQueryString();
    });
