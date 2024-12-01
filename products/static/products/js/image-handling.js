document.addEventListener('DOMContentLoaded', function() {
    // Get the file input and preview elements
    const newImageInput = document.getElementById('new-image');
    const filenameDisplay = document.getElementById('filename');
    const imagePreview = document.getElementById('image-preview');
    const previewImage = document.getElementById('preview-image');

    if (newImageInput) {
        newImageInput.addEventListener('change', function() {
            const file = this.files[0];
            
            // Display filename
            filenameDisplay.textContent = file ? file.name : '';
            
            // Handle image preview
            if (file) {
                // Check if file is an image
                if (!file.type.startsWith('image/')) {
                    filenameDisplay.textContent = 'Please select an image file';
                    imagePreview.style.display = 'none';
                    this.value = ''; // Clear the input
                    return;
                }

                // Show preview
                const reader = new FileReader();
                reader.onload = function(e) {
                    previewImage.src = e.target.result;
                    imagePreview.style.display = 'block';
                };
                reader.readAsDataURL(file);
            } else {
                imagePreview.style.display = 'none';
            }
        });
    }

    // Handle the remove image checkbox
    const removeImageCheckbox = document.querySelector('input[name$="-clear"]');
    if (removeImageCheckbox) {
        removeImageCheckbox.addEventListener('change', function() {
            if (this.checked) {
                imagePreview.style.display = 'none';
                if (newImageInput) newImageInput.value = '';
                if (filenameDisplay) filenameDisplay.textContent = '';
            }
        });
    }
});
