from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse

# Import require_POST decorator
from django.views.decorators.http import require_POST

from .forms import OrderForm
from .models import Order, OrderLineItem, DiscountCode

from products.models import Product
from profiles.models import UserProfile
from profiles.forms import UserProfileForm
from bag.contexts import bag_contents

import stripe
import json


def apply_discount(request, total):
    discount_code = request.POST.get('discount_code')
    if discount_code:
        try:
            discount = DiscountCode.objects.get(
                code=discount_code,
                active=True
            )

            # Get the current shopping bag from the session
            bag = request.session.get('bag', {})

            # Check if discount applies to any items in the bag
            for item_id, item_data in bag.items():
                product = get_object_or_404(Product, pk=item_id)
                if product in discount.products.all():
                    if isinstance(item_data, int):
                        # Simple item without size
                        quantity = item_data
                    else:
                        # Item with size
                        quantity = item_data['items_by_size'].values()

                    item_total = quantity * product.price
                    item_discount = (
                        item_total * discount.discount_percentage
                    ) / 100
                    total -= item_discount

            return total
        except DiscountCode.DoesNotExist:
            messages.error(request, 'Invalid discount code')
    return total


@require_POST
def cache_checkout_data(request):
    try:
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            'bag': json.dumps(request.session.get('bag', {})),
            'save_info': request.POST.get('save_info'),
            'username': (request.user.username 
                        if request.user.is_authenticated else None),
        })
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(
            request,
            'Sorry, your payment cannot be processed right now. '
            'Please try again later.'
        )
        return HttpResponse(content=str(e), status=400)


def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY
    bag = request.session.get('bag', {})

    if request.method == 'POST':
        form_data = {
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
            'country': request.POST['country'],
            'postcode': request.POST['postcode'],
            'town_or_city': request.POST['town_or_city'],
            'street_address1': request.POST['street_address1'],
            'street_address2': request.POST['street_address2'],
            'county': request.POST['county'],
            'discount_code': request.POST.get('discount_code', '')
        }

        order_form = OrderForm(form_data)

        if order_form.is_valid():
            order = order_form.save(commit=False)
            pid = request.POST.get('client_secret').split('_secret')[0]
            order.stripe_pid = pid
            order.original_bag = json.dumps(bag)

            # Calculate initial total
            current_bag = bag_contents(request)
            total = current_bag['grand_total']

            # Apply discount if code provided and save relationship
            if 'discount_code' in request.POST:
                try:
                    discount = DiscountCode.objects.get(
                        code=request.POST['discount_code'],
                        active=True
                    )
                    total = apply_discount(request, total)
                    order.discount = discount
                except DiscountCode.DoesNotExist:
                    messages.error(
                        request,
                        "Invalid or inactive discount code."
                    )
                    return redirect(reverse('checkout'))

            # Update order total after discount
            order.order_total = total
            order.save()

            # Create order line items..
            for item_id, item_data in bag.items():
                try:
                    product = Product.objects.get(id=item_id)
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_line_item.save()
                    else:
                        # Fixes has size bug from shopping bag and products
                        for size, quantity in (
                            item_data['items_by_size'].items()
                        ):
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
                            order_line_item.save()
                except Product.DoesNotExist:
                    messages.error(
                        request,
                        "One of the products in your bag wasn't found "
                        "in our database."
                    )
                    order.delete()
                    return redirect(reverse('view_bag'))

            # Create Stripe payment intent with discounted total
            stripe_total = round(total * 100)
            stripe.api_key = stripe_secret_key
            intent = stripe.PaymentIntent.create(
                amount=stripe_total,
                currency=settings.STRIPE_CURRENCY,
            )

            # If user is authenticated, associate order with their profile
            if request.user.is_authenticated:
                profile = UserProfile.objects.get(user=request.user)
                order.user_profile = profile
                order.save()

            request.session['save_info'] = 'save-info' in request.POST
            return redirect(
                reverse('checkout_success', args=[order.order_number])
            )
        # Handle form validation errors
        for field, errors in order_form.errors.items():
            for error in errors:
                if field == 'phone_number':
                    messages.error(request, f"Phone number error: {error}")
                elif field == 'postcode':
                    messages.error(request, f"Postcode error: {error}")
                elif field == 'discount_code':
                    messages.error(request, f"Discount code error: {error}")
                else:
                    messages.error(
                        request,
                        f"{field.replace('_', ' ').title()}: "
                        f"{error}"
                    )
        return redirect(reverse('checkout'))

    bag = request.session.get('bag', {})
    if not bag:
        messages.error(request, "There's nothing in your bag at the moment.")
        return redirect(reverse('products'))

    # Apply discount if in session
    if 'discount_code' in request.session:
        try:
            discount = DiscountCode.objects.get(
                code=request.session['discount_code'],
                active=True
            )
            total = apply_discount(request, total)
        except DiscountCode.DoesNotExist:
            # Remove invalid discount from session
            del request.session['discount_code']

    current_bag = bag_contents(request)
    total = current_bag['grand_total']

    stripe_total = round(total * 100)
    stripe.api_key = stripe_secret_key
    intent = stripe.PaymentIntent.create(
        amount=stripe_total,
        currency=settings.STRIPE_CURRENCY,
    )

    # Attempt to prefill the form with any info 
    # the user maintains in their profile
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
            order_form = OrderForm(initial={
                'full_name': profile.user.get_full_name(),
                'email': profile.user.email,
                'phone_number': profile.default_phone_number,
                'country': profile.default_country,
                'postcode': profile.default_postcode,
                'town_or_city': profile.default_town_or_city,
                'street_address1': profile.default_street_address1,
                'street_address2': profile.default_street_address2,
                'county': profile.default_county,
            })
        except UserProfile.DoesNotExist:
            order_form = OrderForm()
    else:
        order_form = OrderForm()

    if not stripe_public_key:
        messages.warning(
            request,
            'Stripe public key is missing. '
            'Did you forget to set it in your environment?'
        )

    template = 'checkout/checkout.html'

    # Calculate discount total
    discount_total = (
        current_bag['grand_total'] - total
        if ('discount_code' in request.POST or
            'discount_code' in request.session)
        else 0
    )

    context = {
        'order_form': order_form,
        'discount_total': discount_total,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
    }

    return render(request, template, context)


def checkout_success(request, order_number):
    """Handle successful checkouts
    """
    save_info = request.session.get('save_info')
    order = get_object_or_404(Order, order_number=order_number)

    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)
        # Attach the user's profile to the order
        order.user_profile = profile
        order.save()

        # Save the user's info
        if save_info:
            profile_data = {
                'default_phone_number': order.phone_number,
                'default_country': order.country,
                'default_postcode': order.postcode,
                'default_town_or_city': order.town_or_city,
                'default_street_address1': order.street_address1,
                'default_street_address2': order.street_address2,
                'default_county': order.county,
            }
            user_profile_form = UserProfileForm(profile_data, instance=profile)
            if user_profile_form.is_valid():
                user_profile_form.save()

    success_message = (
        f'Order successfully processed! '
        f'Your order number is {order_number}. '
        f'A confirmation email will be sent to {order.email}.'
    )
    messages.success(request, success_message)

    if 'bag' in request.session:
        del request.session['bag']

    template = 'checkout/checkout_success' + '.html'
    context = {
        'order': order,
    }

    return render(request, template, context)
