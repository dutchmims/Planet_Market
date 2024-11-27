from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models.functions import Lower
from .models import Product, Category, Review, ProductVariant
from .forms import ProductForm, ReviewForm
from django.db import models
import os
from django.conf import settings

def get_product_image_url(product):
    """Helper function to get product image URL with fallback"""
    if product.image:
        try:
            # Check if file exists
            image_path = os.path.join(settings.MEDIA_ROOT, str(product.image))
            if os.path.isfile(image_path):
                return product.image.url
        except Exception:
            pass
    return os.path.join(settings.MEDIA_URL, 'noimage.png')

def all_products(request):
    """ A view to show all products, including sorting and search queries """

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
                products = products.annotate(lower_name=Lower('name'))
            if sortkey == 'category':
                sortkey = 'category__name'
            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            products = products.order_by(sortkey)
            
        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            products = products.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('products'))
            
            queries = Q(name__icontains=query) | Q(description__icontains=query)
            products = products.filter(queries)

    # Process image URLs for all products
    for product in products:
        product.safe_image_url = get_product_image_url(product)

    current_sorting = f'{sort}_{direction}'

    context = {
        'products': products,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
    }

    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    """ A view to show individual product details and handle reviews """

    product = get_object_or_404(Product, pk=product_id)
    # Add safe image URL
    product.safe_image_url = get_product_image_url(product)
    
    reviews = product.reviews.all().order_by('-created_at')
    has_sizes = product.variants.exists()
    form = ReviewForm()

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            
            # Additional validation
            rating = form.cleaned_data.get('rating')
            if rating is not None and (rating < 1.0 or rating > 5.0):
                messages.error(request, 'Rating must be between 1.0 and 5.0')
                return redirect(reverse('product_detail', args=[product.id]))
            
            try:
                review.save()
                
                # Update product rating
                avg_rating = product.reviews.aggregate(models.Avg('rating'))['rating__avg']
                if avg_rating:
                    product.rating = round(avg_rating, 1)
                    product.save(update_fields=['rating'])
                
                messages.success(request, 'Thank you! Your review has been submitted successfully.')
                return redirect(reverse('product_detail', args=[product.id]))
            except Exception as e:
                messages.error(request, f'Error saving review: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')

    context = {
        'product': product,
        'reviews': reviews,
        'form': form,
        'has_sizes': has_sizes,
    }

    return render(request, 'products/product_detail.html', context)


@login_required
def add_product(request):
    """ Add a product to the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Successfully added product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to add product. Please ensure the form is valid.')
    else:
        form = ProductForm()
        
    template = 'products/add_product.html'
    context = {
        'form': form,
    }

    return render(request, template, context)


@login_required
def edit_product(request, product_id):
    """ Edit a product in the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            # Handle ProductVariant update or deletion if needed
            size = form.cleaned_data.get('size')
            color = form.cleaned_data.get('color')
            if size and color:
                # Update existing ProductVariant or create new one
                product_variant, created = ProductVariant.objects.update_or_create(
                    product=product,
                    defaults={'size': size, 'color': color}
                )
            else:
                # If size and color are not provided, delete existing ProductVariant if it exists
                ProductVariant.objects.filter(product=product).delete()
            
            messages.success(request, 'Successfully updated product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to update product. Please ensure the form is valid.')
    else:
        form = ProductForm(instance=product)
        messages.info(request, f'You are editing {product.name}')

    template = 'products/edit_product.html'
    context = {
        'form': form,
        'product': product,
    }

    return render(request, template, context)


@login_required
def delete_product(request, product_id):
    """ Delete a product from the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    messages.success(request, 'Product deleted!')
    return redirect(reverse('products'))
