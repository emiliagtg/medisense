$(document).ready(function () {
    function appendMessage(message, sender) {
        const chatBox = $('#messageContainer');
        const messageDiv = $('<div></div>').addClass('msg ' + sender).text(message);
        chatBox.append(messageDiv);
        chatBox.scrollTop(chatBox[0].scrollHeight);
    }

    $('#textForm').submit(function (e) {
        e.preventDefault();
        const userMessage = $('#text').val();
        appendMessage(userMessage, 'user');
        $('#text').val('');
        $.ajax({
            url: "/get_text_response",
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({ message: userMessage }),
            success: function (response) {
                const botMessage = response.response;
                appendMessage(botMessage, 'bot');
            },
            error: function () {
                appendMessage("Error processing message.", 'bot');
            }
        });
    });

    $('#imageForm').submit(function (e) {
        e.preventDefault();
        const formData = new FormData();
        formData.append("image", $('#inputImage')[0].files[0]);
        $.ajax({
            url: "/upload_image",
            method: "POST",
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                const condition = response.condition;
                const firstAid = response.first_aid;
                appendMessage(`Detected Condition: ${condition}`, 'bot');
                appendMessage(`First Aid: ${firstAid}`, 'bot');
            },
            error: function () {
                appendMessage("Error processing image.", 'bot');
            }
        });
    });

    let videoElement = document.getElementById('video');
    let canvasElement = document.getElementById('canvas');
    let captureButton = document.getElementById('captureBtn');
    let ctx = canvasElement.getContext('2d');

    async function startCamera() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            videoElement.srcObject = stream;
        } catch (err) {
            alert("Error accessing camera: " + err);
        }
    }

    function captureImage() {
        canvasElement.width = videoElement.videoWidth;
        canvasElement.height = videoElement.videoHeight;
        ctx.drawImage(videoElement, 0, 0, canvasElement.width, canvasElement.height);
        const imageData = canvasElement.toDataURL('image/png');
        sendImageToServer(imageData);
    }

    function sendImageToServer(imageData) {
        $.ajax({
            url: '/upload_image',  
            method: 'POST',
            data: { image: imageData },
            success: function(response) {
                console.log("Image successfully uploaded", response);
                displayBotMessage(response.condition, response.first_aid);
            },
            error: function() {
                console.log("Error uploading image");
            }
        });
    }

    function displayBotMessage(condition, firstAid) {
        const chatBox = document.getElementById('chatBox');
        const botMessage = `
            <div class="bot-message">
                <strong>Detected Condition:</strong> ${condition} <br>
                <strong>First Aid:</strong> ${firstAid}
            </div>
        `;
        chatBox.innerHTML += botMessage;
        chatBox.scrollTop = chatBox.scrollHeight;
    }
    startCamera();
    if (captureButton) {
        captureButton.addEventListener('click', captureImage);
    }

    $(document).ready(function () {
        $('#textForm').submit(function (e) {
            e.preventDefault();
            const userMessage = $('#text').val();
            appendMessage(userMessage, 'user');
            $('#text').val('');
            $.ajax({
                url: "/get_text_response",
                method: "POST",
                contentType: "application/json",
                data: JSON.stringify({ message: userMessage }),
                success: function (response) {
                    const botMessage = response.response;
                    appendMessage(botMessage, 'bot');
                },
                error: function () {
                    appendMessage("Error processing message.", 'bot');
                }
            });
        });

        $('#imageForm').submit(function (e) {
            e.preventDefault();
            const formData = new FormData();
            formData.append("image", $('#inputImage')[0].files[0]);
            $.ajax({
                url: "/upload_image",
                method: "POST",
                data: formData,
                processData: false,
                contentType: false,
                success: function (response) {
                    const condition = response.condition;
                    const firstAid = response.first_aid;
                    appendMessage(`Detected Condition: ${condition}`, 'bot');
                    appendMessage(`First Aid: ${firstAid}`, 'bot');
                },
                error: function () {
                    appendMessage("Error processing image.", 'bot');
                }
            });
        });
    });
});

let videoElement = document.getElementById('video');
let canvasElement = document.getElementById('canvas');
let captureButton = document.getElementById('capture');
let ctx = canvasElement.getContext('2d');
async function startCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        videoElement.srcObject = stream;
    } catch (err) {
        alert("Error accessing camera: " + err);
    }
}

function resizeImage(imageData, maxWidth, maxHeight) {
    return new Promise((resolve, reject) => {
        const img = new Image();
        img.src = imageData;
        img.onload = function () {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            let width = img.width;
            let height = img.height;

            if (width > maxWidth || height > maxHeight) {
                const ratio = Math.min(maxWidth / width, maxHeight / height);
                width = width * ratio;
                height = height * ratio;
            }

            canvas.width = width;
            canvas.height = height;
            ctx.drawImage(img, 0, 0, width, height);

            resolve(canvas.toDataURL('image/jpeg', 0.7)); 
        };
        img.onerror = reject;
    });
}

function captureImage() {
    const video = document.getElementById('video');
    canvasElement.width = video.videoWidth;
    canvasElement.height = video.videoHeight;

    ctx.drawImage(video, 0, 0, canvasElement.width, canvasElement.height);

    const imageData = canvasElement.toDataURL('image/png');  
    resizeImage(imageData, 800, 600)
        .then(resizedImage => {
            sendImageToServer(resizedImage);
        })
        .catch(err => {
            console.error("Error resizing image:", err);
        });
}

function sendImageToServer(resizedImage) {
    $.ajax({
        url: '/upload_image',  
        method: 'POST',
        data: { image: resizedImage },
        success: function(response) {
            console.log("Image successfully uploaded", response);
            displayBotMessage(response.condition, response.first_aid);
        },
        error: function() {
            console.log("Error uploading image");
        }
    });
}

function displayBotMessage(condition, firstAid) {
    const chatBox = document.getElementById('chatBox');
    const botMessage = `
        <div class="bot-message">
            <strong>Detected Condition:</strong> ${condition} <br>
            <strong>First Aid:</strong> ${firstAid}
        </div>
    `;
    chatBox.innerHTML += botMessage;
    chatBox.scrollTop = chatBox.scrollHeight;
}

captureButton.addEventListener('click', captureImage);
window.onload = startCamera;