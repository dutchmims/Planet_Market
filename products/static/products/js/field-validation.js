// Basic product field validation
document.addEventListener('DOMContentLoaded', function() {
    // Price validation
    const priceInput = document.getElementById('id_price');
    if (priceInput) {
        priceInput.addEventListener('input', function() {
            const price = parseFloat(this.value);
            if (isNaN(price) || price < 0.01) {
                this.classList.add('is-invalid');
                this.classList.remove('is-valid');
            } else {
                this.classList.add('is-valid');
                this.classList.remove('is-invalid');
            }
        });
    }

    // Rating validation
    const ratingInput = document.getElementById('id_rating');
    if (ratingInput) {
        ratingInput.addEventListener('input', function() {
            const rating = parseFloat(this.value);
            if (isNaN(rating) || rating < 0 || rating > 5) {
                this.classList.add('is-invalid');
                this.classList.remove('is-valid');
            } else {
                this.classList.add('is-valid');
                this.classList.remove('is-invalid');
            }
        });
    }
});