const inputEditor = ace.edit("inputEditor");
const outputEditor = ace.edit("outputEditor");

[inputEditor, outputEditor].forEach(editor => {
    editor.setTheme("ace/theme/twilight");
    editor.session.setMode("ace/mode/text");
    editor.setShowPrintMargin(false);
    editor.setFontSize(14);
});
outputEditor.setReadOnly(true);

const elements = {
  dropZone: document.getElementById("dropZone"),
  dropText: document.getElementById("dropText"),
  fileName: document.getElementById("fileName"),
  fileInput: document.getElementById("fileInput"),
  convertBtn: document.getElementById("convertBtn"),
  downloadBtn: document.getElementById("downloadBtn"),
  copyBtn: document.getElementById("copyBtn"),
  themeToggle: document.getElementById("themeToggle"),
  srcFormat: document.getElementById("srcFormat"),
  dstFormat: document.getElementById("dstFormat"),
  validationStatus: document.getElementById("validationStatus"),
  historyList: document.getElementById("historyList"),
  clearHistory: document.getElementById("clearHistory")
};

let resultData = "";
let resultExt = "";

// Тема
// Исправленная функция применения темы
function applyTheme(isLight) {
    const themeName = isLight ? "chrome" : "twilight";
    
    // Ключевое исправление здесь:
    if (isLight) {
        document.body.setAttribute("data-theme", "light");
    } else {
        document.body.removeAttribute("data-theme");
    }
    
    elements.themeToggle.textContent = isLight ? "🌙" : "☀️";
    
    // Обновляем темы в редакторах Ace
    if (inputEditor && outputEditor) {
        inputEditor.setTheme(`ace/theme/${themeName}`);
        outputEditor.setTheme(`ace/theme/${themeName}`);
    }
}

// Исправленный клик по кнопке
elements.themeToggle.onclick = () => {
    // Проверяем, стоит ли сейчас светлая тема
    const isCurrentlyLight = document.body.getAttribute("data-theme") === "light";
    const newThemeIsLight = !isCurrentlyLight; // Инвертируем
    
    localStorage.setItem("theme", newThemeIsLight ? "light" : "dark");
    applyTheme(newThemeIsLight);
};

inputEditor.session.on('change', () => {
    if (elements.srcFormat.value === 'json' && inputEditor.getValue().trim()) {
        try {
            JSON.parse(inputEditor.getValue());
            showValidation(true, "JSON Valid");
        } catch {
            showValidation(false, "JSON Error");
        }
    } else {
        elements.validationStatus.classList.add("hidden");
    }
});

function showValidation(isValid, text) {
    elements.validationStatus.className = `badge ${isValid ? 'valid' : 'invalid'}`;
    elements.validationStatus.textContent = text;
}

elements.dropZone.onclick = () => elements.fileInput.click();
elements.fileInput.onchange = () => handleFile(elements.fileInput.files[0]);

function handleFile(file) {
    if (!file) return;
    elements.fileName.textContent = file.name;
    elements.dropZone.classList.add("selected");
    autoDetectFormat(file.name);
    const reader = new FileReader();
    reader.onload = () => inputEditor.setValue(reader.result, -1);
    reader.readAsText(file);
}

function autoDetectFormat(name) {
    const ext = name.split(".").pop().toLowerCase();
    const map = { csv: "csv", json: "json", yaml: "yaml", yml: "yaml" };
    if (map[ext]) {
        elements.srcFormat.value = map[ext];
        elements.srcFormat.onchange();
    }
}

elements.srcFormat.onchange = () => inputEditor.session.setMode(`ace/mode/${elements.srcFormat.value}`);
elements.dstFormat.onchange = () => outputEditor.session.setMode(`ace/mode/${elements.dstFormat.value}`);

elements.convertBtn.onclick = async () => {
    const content = inputEditor.getValue();
    if (!content.trim()) return alert("Введите данные");

    setLoading(true);
    const formData = new FormData();
    formData.append("text", content);
    formData.append("src_format", elements.srcFormat.value);
    formData.append("dst_format", elements.dstFormat.value);

    try {
        const res = await fetch("/convert", { method: "POST", body: formData });
        if (!res.ok) throw new Error();
        resultData = await res.text();
        resultExt = elements.dstFormat.value;
        outputEditor.setValue(resultData, -1);
        elements.dstFormat.onchange();
        elements.downloadBtn.disabled = elements.copyBtn.disabled = false;
        addToHistory(elements.fileName.textContent || "Manual Input", elements.srcFormat.value, resultExt, resultData);
    } catch {
        alert("Ошибка конвертации");
    } finally {
        setLoading(false);
    }
};

function setLoading(isLoading) {
    elements.convertBtn.disabled = isLoading;
    elements.convertBtn.querySelector(".loader").classList.toggle("hidden", !isLoading);
}

function addToHistory(name, src, dst, data) {
    const history = JSON.parse(localStorage.getItem("convertHistory") || "[]");
    history.unshift({ id: Date.now(), name, src, dst, timestamp: new Date().toLocaleTimeString(), preview: data });
    localStorage.setItem("convertHistory", JSON.stringify(history.slice(0, 5)));
    renderHistory();
}

function renderHistory() {
    const history = JSON.parse(localStorage.getItem("convertHistory") || "[]");
    elements.historyList.innerHTML = history.length ? "" : '<div class="empty-history">Пусто</div>';
    history.forEach(item => {
        const div = document.createElement("div");
        div.className = "history-item";
        div.innerHTML = `<div class="history-meta"><span>${item.timestamp}</span><span>${item.src} ➝ ${item.dst}</span></div><div class="history-name">${item.name}</div>`;
        div.onclick = () => {
            outputEditor.setValue(item.preview, -1);
            elements.downloadBtn.disabled = elements.copyBtn.disabled = false;
        };
        elements.historyList.appendChild(div);
    });
}

elements.clearHistory.onclick = () => { localStorage.removeItem("convertHistory"); renderHistory(); };
renderHistory();

elements.downloadBtn.onclick = () => {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([resultData]));
    a.download = `result.${resultExt}`;
    a.click();
};

elements.copyBtn.onclick = () => {
    navigator.clipboard.writeText(resultData);
    elements.copyBtn.textContent = "✅";
    setTimeout(() => elements.copyBtn.textContent = "Копировать", 1500);
};