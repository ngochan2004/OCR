export async function runOCR(file, gt, lang) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("ground_truth", gt);
    formData.append("lang", lang);

    const res = await fetch("http://localhost:8000/ocr", {
        method: "POST",
        body: formData,
    });

    return await res.json();
}
