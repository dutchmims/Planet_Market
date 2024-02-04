from django.shortcuts import render, redirect, reverse
from django.contrib import messages

from .forms import OrderForm


def checkout(request):
    bag = request.session.get('bag', {})
    if not bag:
        messages.error(request, "There's nothing in your bag at the moment")
        return redirect(reverse('products'))

    order_form = OrderForm()
    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': 'pk_test_51OgDfTCSVsESJyem25ugNm6eiJz2KUZ4G5rorQM8HsN05FWh7UpY5QTiZpR83Et7kgYLzAHe62tKC0M1BGB8bg4F00hPIfVJ6L',
        'client_secret': 'test client secret',
    }

    return render(request, template, context)
