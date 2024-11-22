from django import forms
from .widgets import CustomClearableFileInput
from .models import Product, Category, Review, ProductVariant


class ProductForm(forms.ModelForm):
    size = forms.CharField(max_length=50, required=False)  # Optional field for size
    color = forms.CharField(max_length=50, required=False)  # Optional field for color

    class Meta:
        model = Product
        fields = '__all__'

    image = forms.ImageField(label='Image', required=False, widget=CustomClearableFileInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.objects.all()
        friendly_names = [(c.id, c.get_friendly_name()) for c in categories]

        self.fields['category'].choices = friendly_names
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'

    def save(self, commit=True):
        product = super().save(commit=False)
        if commit:
            product.save()
            # Create ProductVariant instance if size and color are provided
            size = self.cleaned_data.get('size')
            color = self.cleaned_data.get('color')
            if size and color:
                ProductVariant.objects.create(product=product, size=size, color=color)
        return product


class ReviewForm(forms.ModelForm):

    class Meta:
        model = Review
        fields = ['user_name', 'review_text', 'rating']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'
