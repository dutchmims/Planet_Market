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
    rating = forms.DecimalField(
        min_value=1.0,
        max_value=5.0,
        decimal_places=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control border-black rounded-0',
            'step': '0.5',
            'min': '1.0',
            'max': '5.0'
        })
    )

    class Meta:
        model = Review
        fields = ['user_name', 'review_text', 'rating']
        widgets = {
            'user_name': forms.TextInput(attrs={
                'class': 'form-control border-black rounded-0',
                'placeholder': 'Your Name'
            }),
            'review_text': forms.Textarea(attrs={
                'class': 'form-control border-black rounded-0',
                'placeholder': 'Write your review here...',
                'rows': 4
            })
        }
        error_messages = {
            'rating': {
                'min_value': 'Rating must be at least 1.0',
                'max_value': 'Rating cannot exceed 5.0',
                'invalid': 'Please enter a valid rating between 1.0 and 5.0'
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control border-black rounded-0'
            field.error_messages = {'required': f'{field_name.replace("_", " ").title()} is required'}
