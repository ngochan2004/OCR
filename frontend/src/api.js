export async function runOCR(file, gt, lang) {
    const formData = new FormData();
    formData.append("file", file);
    if (gt) formData.append("gt_text", gt);
    formData.append("lang", lang);

    const res = await fetch("http://localhost:8000/ocr", {
        method: "POST",
        body: formData,
    });

    return await res.json();
}
