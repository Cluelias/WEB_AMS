importScripts('https://cdn.jsdelivr.net/npm/@zxing/library@1.10.1/index.min.js');

const codeReader = new ZXing.BrowserQRCodeReader();

onmessage = function (event) {
    const imageData = event.data;

    try {
        const luminanceSource = new ZXing.HTMLCanvasElementLuminanceSource(imageData);
        const binaryBitmap = new ZXing.BinaryBitmap(new ZXing.HybridBinarizer(luminanceSource));
        const result = codeReader.decode(binaryBitmap);
        postMessage(result.text);
    } catch (e) {
        postMessage(null);
    }
};
