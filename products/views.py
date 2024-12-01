"""Views for managing products in the store."""

# Django imports
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models.functions import Lower
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.urls import reverse

# Local imports
from planet_market.utils import is_staff_member
from .forms import (
    ProductForm,
    ReviewForm,
)
from .models import (
    Product,
    ProductVariant,
    Review,
)


def all_products(request):
    """A view to show all products, including
    sorting and search queries"""
    products = Product.objects.all()
    query = None
    categories = None
    sort = None
    direction = None

    if request.GET:
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'name':
                sortkey = 'lower_name'
                products = products.annotate(
                    lower_name=Lower('name'))
            if sortkey == 'category':
                sortkey = 'category__name'
            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            products = products.order_by(sortkey)

        if 'category' in request.GET:
            categories = request.GET['category'].\
                split(',')
            products = products.filter(
                category__name__in=categories)

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(
                    request,
                    "You didn't enter any search criteria!"
                )
                return redirect(reverse('products'))

            queries = Q(name__icontains=query) |\
                Q(description__icontains=query)
            products = products.filter(queries)

    current_sorting = f'{sort}_{direction}' if sort and\
        direction else None

    context = {
        'products': products,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
    }

    return render(request,
                  'products/products.html',
                  context)


def product_detail(request, product_id):
    """A view to show individual product details"""
    product = get_object_or_404(Product,
                                pk=product_id)
    reviews = Review.objects.filter(
        product=product)
    review_form = ReviewForm()

    if request.method == 'POST' and \
        request.user.is_authenticated:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(
                commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request,
                             'Successfully added review!')
            return redirect(
                reverse(
                    'product_detail',
                    args=[product.id]))
        messages.error(
            request,
            'Failed to add review. Please ensure the '
            + 'form is valid.'
        )
    context = {
        'product': product,
        'reviews': reviews,
        'form': review_form,
    }

    return render(request,
                  'products/product_detail.html',
                  context)


@login_required
def add_product(request):
    """Add a product to the store"""
    if not is_staff_member(request.user):
        messages.error(
            request,
            'Sorry, only staff members can do that.'
        )
        return redirect(reverse('home'))

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request,
                             'Successfully added product!')
            return redirect(reverse('product_detail',
                                    args=[product.id]))
        messages.error(
            request,
            'Failed to add product. Please ensure the '
            + 'form is valid.'
        )
    else:
        form = ProductForm()

    template = 'products/add_product.html'
    context = {
        'form': form,
    }

    return render(request, template, context)


@login_required
def edit_product(request, product_id):
    """Edit a product in the store"""
    if not is_staff_member(request.user):
        messages.error(
            request,
            'Sorry, only staff members can do that.'
        )
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES,
                           instance=product)
        if form.is_valid():
            product = form.save()

            # Handle variant data
            variant = product.variants.first()
            if not variant:
                variant = ProductVariant(product=product)

            variant.size = request.POST.get('size', '')
            variant.color = request.POST.get('color', '')
            variant.sku = f"{product.sku}" \
                        f"-{variant.size}-{variant.color}" \
                        if product.sku else ""
            variant.save()

            messages.success(request,
                            'Successfully updated product!')
            return redirect(reverse(
                'product_detail', args=[product.id]))
        messages.error(
            request,
            'Failed to update product. Please ensure the'
            + ' form is valid.'
        )
    else:
        form = ProductForm(instance=product)
        messages.info(request,
                    f'You are editing {product.name}')

    template = 'products/edit_product.html'
    context = {
        'form': form,
        'product': product,
    }

    return render(request, template, context)


@login_required
def delete_product(request, product_id):
    """Delete a product from the store"""
    if not is_staff_member(request.user):
        messages.error(
            request,
            'Sorry, only staff members can do that.'
        )
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    messages.success(request, 'Product deleted!')
    return redirect(reverse('products'))


@login_required
def manage_products(request):
    """A view to manage products - for staff only"""
    if not is_staff_member(request.user):
        messages.error(
            request,
            'Sorry, only staff members can do that.'
        )
        return redirect(reverse('home'))

    products = Product.objects.all().order_by('name')

    template = 'products/manage_products.html'
    context = {
        'products': products,
    }

    return render(request, template, context)
