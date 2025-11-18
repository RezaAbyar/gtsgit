// تنظیمات QuaggaJS
function startscan() {
    document.getElementById("endscan").style.display = "block";
    document.getElementById("camera").style.display = "block";
    document.getElementById("startscan").style.display = "none";
    Quagga.init({
        inputStream: {
            name: "Live", type: "LiveStream", target: document.querySelector('#camera'), constraints: {
                width: 440, height: 280, facingMode: "environment" // استفاده از دوربین پشتی
            },
        }, decoder: {
            readers: ["ean_reader", "code_128_reader"] // انواع بارکدهای قابل تشخیص
        }
    }, function (err) {
        if (err) {
            console.error(err);
            return;
        }
        console.log("QuaggaJS initialized successfully.");
        Quagga.start();
    });

    // تشخیص بارکد
    Quagga.onDetected(function (result) {
        const barcode = result.codeResult.code;
        document.getElementById('id_init').value = barcode;
        document.getElementById("endscan").style.display = "none";
        document.getElementById("camera").style.display = "none";
        document.getElementById("startscan").style.display = "block";
        Quagga.stop(); // توقف اسکن پس از تشخیص
    });
}

function endscan() {
    document.getElementById("endscan").style.display = "none";
    document.getElementById("camera").style.display = "none";
    document.getElementById("startscan").style.display = "block";
    Quagga.stop();
}
