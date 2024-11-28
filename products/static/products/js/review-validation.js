document.addEventListener('DOMContentLoaded', function() {
    const reviewForm = document.querySelector('form');
    if (!reviewForm) return;

    const ratingInput = reviewForm.querySelector('input[name="rating"]');
    const userNameInput = reviewForm.querySelector('input[name="user_name"]');
    const reviewTextArea = reviewForm.querySelector('textarea[name="review_text"]');

    function showError(input, message) {
        const errorDiv = input.nextElementSibling || document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        if (!input.nextElementSibling) {
            input.parentNode.insertBefore(errorDiv, input.nextSibling);
        }
        input.classList.add('is-invalid');
        input.classList.remove('is-valid');
    }

    function showSuccess(input) {
        const errorDiv = input.nextElementSibling;
        if (errorDiv && errorDiv.className === 'invalid-feedback') {
            errorDiv.remove();
        }
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
    }

    function validateRating() {
        const rating = parseFloat(ratingInput.value);
        if (isNaN(rating)) {
            showError(ratingInput, 'Please enter a valid rating');
            return false;
        }
        if (rating < 1.0) {
            showError(ratingInput, 'Rating must be at least 1.0');
            return false;
        }
        if (rating > 5.0) {
            showError(ratingInput, 'Rating cannot exceed 5.0');
            return false;
        }
        showSuccess(ratingInput);
        return true;
    }

    function validateUserName() {
        const userName = userNameInput.value.trim();
        if (userName.length < 2) {
            showError(userNameInput, 'Name must be at least 2 characters long');
            return false;
        }
        showSuccess(userNameInput);
        return true;
    }

    function validateReviewText() {
        const reviewText = reviewTextArea.value.trim();
        if (reviewText.length < 10) {
            showError(reviewTextArea, 'Review must be at least 10 characters long');
            return false;
        }
        showSuccess(reviewTextArea);
        return true;
    }

    // Real-time validation
    if (ratingInput) {
        ratingInput.addEventListener('input', validateRating);
        ratingInput.addEventListener('change', validateRating);
    }
    if (userNameInput) {
        userNameInput.addEventListener('input', validateUserName);
        userNameInput.addEventListener('blur', validateUserName);
    }
    if (reviewTextArea) {
        reviewTextArea.addEventListener('input', validateReviewText);
        reviewTextArea.addEventListener('blur', validateReviewText);
    }

    // Form submission
    reviewForm.addEventListener('submit', function(e) {
        const isRatingValid = validateRating();
        const isUserNameValid = validateUserName();
        const isReviewTextValid = validateReviewText();

        if (!isRatingValid || !isUserNameValid || !isReviewTextValid) {
            e.preventDefault();
            e.stopPropagation();
        }
    });
});
