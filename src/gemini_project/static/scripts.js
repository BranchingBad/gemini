(function() {
    const submitButton = document.getElementById('submit-button');
    const promptInput = document.getElementById('prompt-input');
    const modelSelect = document.getElementById('model-select');
    const imageUpload = document.getElementById('image-upload');
    const imageStatus = document.getElementById('image-status');
    const spinner = document.getElementById('spinner');
    const buttonText = document.getElementById('button-text');

    let imageBase64Data = null;

    function updateSubmitButtonState() {
        const isPromptValid = promptInput.value.trim().length > 0;
        submitButton.disabled = !isPromptValid;
        if (!isPromptValid) {
            buttonText.textContent = 'Enter a Prompt';
        } else {
            buttonText.textContent = 'Send to Gemini API';
        }
    }

    promptInput.addEventListener('input', updateSubmitButtonState);
    modelSelect.addEventListener('change', updateSubmitButtonState);

    imageUpload.addEventListener('change', (event) => {
        const file = event.target.files[0];
        imageBase64Data = null;
        imageStatus.textContent = 'No image uploaded.';

        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                // The result is a data URL like 'data:image/jpeg;base64,...'
                // We only need the base64 part
                imageBase64Data = e.target.result.split(',')[1];
                imageStatus.textContent = `Image uploaded: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`;
                updateSubmitButtonState();
            };
            reader.onerror = () => {
                showCustomAlert("Error", "Could not read image file.");
            };
            reader.readAsDataURL(file);
        }
    });

    // Initial state check
    updateSubmitButtonState();

    submitButton.addEventListener('click', async () => {
        const model = modelSelect.value;
        const prompt = promptInput.value.trim();

        if (!prompt) {
            showCustomAlert("Error", "Please enter a prompt.");
            return;
        }

        // UI State: Loading
        submitButton.disabled = true;
        spinner.classList.remove('hidden');
        buttonText.textContent = 'Processing...';
        document.getElementById('api-result').textContent = 'Generating response...';
        document.getElementById('duration').textContent = 'Duration: 0.00s';
        document.getElementById('copy-button').style.display = 'none';
        document.getElementById('download-button').style.display = 'none';
        document.getElementById('api-result').classList.add('response-text');


        try {
            const response = await fetch('/gemini_call', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    model: model,
                    prompt: prompt,
                    image_data: imageBase64Data // Will be null if no file uploaded
                })
            });

            const data = await response.json();

            if (response.ok) {
                processResult(data);
            } else {
                throw new Error(data.error || 'Server error occurred.');
            }
        } catch (error) {
            console.error('Fetch error:', error);
            document.getElementById('api-result').textContent = `Error: ${error.message}`;
            showCustomAlert("API Error", error.message);
        } finally {
            // UI State: Done
            spinner.classList.add('hidden');
            updateSubmitButtonState(); // Re-enable if prompt is valid
        }
    });


    function showCustomAlert(title, message, isError = false) {
        const alertDiv = document.getElementById('customAlert');
        const alertTitle = document.getElementById('alertTitle');
        const alertMessage = document.getElementById('alertMessage');
        const alertIcon = document.getElementById('alertIcon');

        alertDiv.classList.remove('show', 'bg-green-500', 'bg-red-500');

        if (isError || title.toLowerCase().includes('error') || title.toLowerCase().includes('failed')) {
            alertDiv.classList.add('bg-red-500');
            alertIcon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>';
        } else {
            alertDiv.classList.add('bg-green-500');
            alertIcon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>';
        }

        alertTitle.textContent = title;
        alertMessage.textContent = message;

        // Show and hide logic
        setTimeout(() => {
            alertDiv.classList.add('show');
        }, 10); // Small delay to ensure transition works
        setTimeout(() => {
            alertDiv.classList.remove('show');
        }, 3000);
    }


    /**
     * Processes the API response data and updates the UI accordingly.
     * This function handles both text and image generation responses.
     */
    function processResult(data) {
        const resultElement = document.getElementById('api-result');
        const resultType = data.result_type;
        const duration = data.duration;
        const textResult = data.result; // This is the image base64 for image type, or text for text type

        document.getElementById('duration').textContent = `Duration: ${duration}s`;

        // Clear previous content
        resultElement.innerHTML = '';
        resultElement.classList.remove('response-text'); // Ensure text formatting is removed for image

        if (resultType === 'image') {
            const imageBase64 = data.result;
            const mimeType = data.mime_type;
            const textResponse = data.text_response;

            // 1. Display the image
            const img = document.createElement('img');
            img.src = `data:${mimeType};base64,${imageBase64}`;
            img.alt = 'Generated Image';
            img.classList.add('w-full', 'h-auto', 'rounded-lg', 'shadow-xl');
            resultElement.appendChild(img);

            // 2. Display the accompanying text response from the model
            if (textResponse) {
                const textHeader = document.createElement('h3');
                textHeader.classList.add('text-lg', 'font-semibold', 'mt-4', 'mb-2', 'text-gray-800');
                textHeader.textContent = 'Model Description (Text Output):';

                const textP = document.createElement('div');
                textP.classList.add('response-text', 'p-3', 'bg-gray-100', 'rounded-md', 'mt-2', 'border', 'border-gray-200');
                textP.textContent = textResponse.trim();

                resultElement.appendChild(textHeader);
                resultElement.appendChild(textP);

                 // Setup copy for text response
                document.getElementById('copy-button').onclick = () => copyToClipboard(textResponse.trim());
                document.getElementById('copy-button').style.display = 'inline-flex';
            } else {
                // Hide copy button if there's no text to copy
                document.getElementById('copy-button').style.display = 'none';
            }

            // Setup download button for the image
            document.getElementById('download-button').onclick = () => {
                const link = document.createElement('a');
                link.href = img.src;
                // Use a generic name with a timestamp for saving
                link.download = `gemini_generated_image_${new Date().getTime()}.png`;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                showCustomAlert("Success!", "Image download started.");
            };
            document.getElementById('download-button').style.display = 'inline-flex';


        } else if (resultType === 'text') {
            // Handle standard text response or image-generation failure text
            resultElement.classList.add('response-text');
            resultElement.textContent = textResult;
            document.getElementById('copy-button').onclick = () => copyToClipboard(textResult);
            document.getElementById('copy-button').style.display = 'inline-flex';
            document.getElementById('download-button').style.display = 'none';
        } else {
            // Handle error responses
            resultElement.classList.add('response-text');
            resultElement.textContent = data.error || "An unknown error occurred.";
            document.getElementById('copy-button').style.display = 'none';
            document.getElementById('download-button').style.display = 'none';
            showCustomAlert("API Error", data.error || "An unknown error occurred.", true);
        }
    }

    // --- Clipboard Copy Logic ---

    function copyToClipboard(textToCopy) {
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(textToCopy).then(() => {
                showCustomAlert("Success!", "Response copied to clipboard.");
            }).catch(err => {
                console.error('Failed to copy text using clipboard API: ', err);
                // Fallback to old method if modern one fails
                fallbackCopyTextToClipboard(textToCopy);
            });
        } else {
            fallbackCopyTextToClipboard(textToCopy);
        }
    }

    function fallbackCopyTextToClipboard(text) {
        const tempTextArea = document.createElement("textarea");
        tempTextArea.value = text;
        // Avoid scrolling to bottom of page in Windows
        tempTextArea.style.position = 'fixed';
        tempTextArea.style.top = 0;
        tempTextArea.style.left = 0;
        document.body.appendChild(tempTextArea);
        tempTextArea.focus();
        tempTextArea.select();
        try {
            document.execCommand('copy');
            showCustomAlert("Success!","Response copied to clipboard (fallback).");
        } catch (err) {
            showCustomAlert("Copy Failed", "Failed to copy text. Please try again.");
        } finally {
            document.body.removeChild(tempTextArea);
        }
    }

    document.addEventListener('DOMContentLoaded', () => {
        fetch('/api/models')
            .then(response => response.json())
            .then(models => {
                modelSelect.innerHTML = ''; // Clear loading message
                models.forEach(model => {
                    // The model name is nested under 'name'
                    const option = document.createElement('option');
                    option.value = model;
                    option.textContent = model;
                    modelSelect.appendChild(option);
                });
                // Set a default model if available
                if (models.length > 0) {
                    modelSelect.value = models.find(m => m.includes('flash')) || models[0];
                }
            })
            .catch(error => {
                console.error('Error fetching models:', error);
                modelSelect.innerHTML = '<option value="">Could not load models</option>';
            });
    });
})();
