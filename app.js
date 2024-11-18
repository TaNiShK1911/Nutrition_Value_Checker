document.getElementById('uploadForm').addEventListener('submit', async function (event) {
    event.preventDefault(); // Prevent the form from submitting the default way

    const imageInput = document.getElementById('imageUpload');
    const resultDiv = document.getElementById('result');
    const scoreSpan = document.getElementById('score');
    const evaluationP = document.getElementById('evaluation');

    // Create a form data object to send the image
    const formData = new FormData();
    formData.append('image', imageInput.files[0]);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            scoreSpan.textContent = data.score.toFixed(2);  // Display score
            evaluationP.textContent = data.score >= 80 
                ? 'This product is nutritious.' 
                : data.score >= 50 
                ? 'This product is average.' 
                : 'This product does not meet standard nutritional guidelines.';

            resultDiv.classList.remove('hidden');  // Show result section
        } else {
            alert('Error analyzing image. Please try again.');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to send image. Check your connection.');
    }
});
