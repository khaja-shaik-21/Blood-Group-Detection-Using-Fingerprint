async function captureFingerprint() {
    const statusElement = document.getElementById('status');
    const loader = document.getElementById('loader');
    const bloodGroupResult = document.getElementById('bloodGroupResult');
    const imgElement = document.getElementById('fingerprint');
    const base64Input = document.getElementById('fingerprint_base64');
    const hasImageInput = document.getElementById('hasImage');

    statusElement.textContent = "Capturing...";
    statusElement.style.display = 'block'; // Show status during capture
    loader.style.display = 'block';
    bloodGroupResult.style.display = 'none';
    hasImageInput.value = 'false'; // Reset image state during capture

    try {
        const response = await fetch('http://localhost:5001/capture_fingerprint');
        const data = await response.json();

        if (data.status === 'success') {
            const base64Image = `data:image/png;base64,${data.image}`;
            imgElement.src = base64Image;
            imgElement.style.display = 'block';
            base64Input.value = base64Image;
            statusElement.textContent = "Capture successful!";
            hasImageInput.value = 'true'; // Set image state after successful capture
        } else {
            statusElement.textContent = data.message || "Capture failed.";
        }
    } catch (error) {
        console.error('Error:', error);
        statusElement.textContent = "Error connecting to scanner service.";
    } finally {
        loader.style.display = 'none';
        setTimeout(() => {
            if (hasImageInput.value === 'true') {
                statusElement.style.display = 'none'; // Hide after capture if image exists
            } else {
                statusElement.textContent = "Place your finger on the scanner or upload an image...";
            }
        }, 2000); // Reset or hide after 2 seconds
    }
}

function previewImage(event) {
    const imgElement = document.getElementById('fingerprint');
    const statusElement = document.getElementById('status');
    const file = event.target.files[0];
    const hasImageInput = document.getElementById('hasImage');

    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            imgElement.src = e.target.result;
            imgElement.style.display = 'block';
            statusElement.style.display = 'none'; // Hide status after upload
            hasImageInput.value = 'true'; // Set image state
        };
        reader.readAsDataURL(file);
    }
}

function updateFileName() {
    const fileInput = document.getElementById('fileInput');
    const fileNameSpan = document.getElementById('fileName');
    if (fileInput.files.length > 0) {
        fileNameSpan.textContent = fileInput.files[0].name;
    } else {
        fileNameSpan.textContent = 'No file chosen';
    }
}

function hideStatus() {
    const statusElement = document.getElementById('status');
    statusElement.style.display = 'none'; // Hide status when file is uploaded
}

document.getElementById('predictionForm').addEventListener('submit', function(event) {
    const loader = document.getElementById('loader');
    const statusElement = document.getElementById('status');
    const hasImageInput = document.getElementById('hasImage');
    loader.style.display = 'block';
    statusElement.style.display = 'none'; // Hide status during detection
    hasImageInput.value = 'true'; // Ensure image state is maintained
});