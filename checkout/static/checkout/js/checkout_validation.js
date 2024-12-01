// Checkout form validation
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('payment-form');
    const submitButton = document.getElementById('submit-button');
    const publicKey = document.getElementById('id_stripe_public_key').textContent.slice(1, -1);
    const clientSecret = document.getElementById('id_client_secret').textContent.slice(1, -1);
    const stripe = Stripe(publicKey);
    const elements = stripe.elements();
    const card = elements.create('card');
    card.mount('#card-element');

    // Phone number validation
    const phoneInput = form.querySelector('input[name="phone_number"]');
    phoneInput.addEventListener('input', function(e) {
        const phone = e.target.value;
        // Allow +, digits, spaces, and hyphens
        const phoneRegex = /^\+?[0-9\s-]{9,17}$/;

        if (!phoneRegex.test(phone)) {
            phoneInput.setCustomValidity('Please enter a valid phone number (min 9 & max 17digits, can include +, spaces, or hyphens)');
        } else {
            phoneInput.setCustomValidity('');
        }
    });

    // Postal code validation for UK, Ireland, and US
    const postalInput = form.querySelector('input[name="postcode"]');
    if (postalInput) {
        postalInput.addEventListener('input', function(e) {
            const postal = e.target.value.toUpperCase();
            // Regex patterns for different postal code formats
            const ukPattern = /^[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][A-Z]{2}$/;  // UK: SW1A 1AA
            const irelandPattern = /^[A-Z][0-9]{2}\s[A-Z0-9]{4}$/;  // Ireland Eircode: D02 AF30 (requires space)
            const usPattern = /^[0-9]{5}(-[0-9]{4})?$/;  // US: 12345 or 12345-6789

            if (!ukPattern.test(postal) && !irelandPattern.test(postal) && !usPattern.test(postal)) {
                postalInput.setCustomValidity('Please enter a valid postal code:\n' +
                    '• UK: e.g., SW1A 1AA\n' +
                    '• Ireland (Eircode): e.g., D02 AF30 (must include space)\n' +
                    '• US: e.g., 90210 or 90210-1234');
            } else {
                postalInput.setCustomValidity('');
            }
        });
    }

    // Handle realtime validation errors on the card element
    card.addEventListener('change', function (event) {
        var errorDiv = document.getElementById('card-errors');
        if (event.error) {
            var html = `
                <span class="icon" role="alert">
                    <i class="fas fa-times"></i>
                </span>
                <span>${event.error.message}</span>
            `;
            errorDiv.innerHTML = html;
        } else {
            errorDiv.textContent = '';
        }
    });

    // Handle form submit
    form.addEventListener('submit', function(ev) {
        ev.preventDefault();

        // Check form validity first
        if (!form.checkValidity()) {
            form.classList.add('was-validated');
            return;
        }

        card.update({ 'disabled': true});
        submitButton.setAttribute('disabled', true);
        
        // Create payment method and confirm payment
        stripe.confirmCardPayment(clientSecret, {
            payment_method: {
                card: card,
                billing_details: {
                    name: form.full_name.value,
                    email: form.email.value,
                    phone: form.phone_number.value,
                    address: {
                        line1: form.street_address1.value,
                        line2: form.street_address2.value,
                        city: form.town_or_city.value,
                        country: form.country.value,
                        state: form.county.value,
                    }
                }
            }
        }).then(function(result) {
            if (result.error) {
                var errorDiv = document.getElementById('card-errors');
                var html = `
                    <span class="icon" role="alert">
                        <i class="fas fa-times"></i>
                    </span>
                    <span>${result.error.message}</span>`;
                errorDiv.innerHTML = html;
                card.update({ 'disabled': false});
                submitButton.removeAttribute('disabled');
            } else {
                if (result.paymentIntent.status === 'succeeded') {
                    form.submit();
                }
            }
        });
    });
});
