from django import forms
from .models import Item, Order, OrderItem


class ItemForm(forms.ModelForm):
    """Form for creating/editing items."""
    
    class Meta:
        model = Item
        fields = ['name', 'description', 'image']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200',
                'placeholder': 'أدخل اسم المادة',
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200',
                'placeholder': 'وصف المادة (اختياري)',
                'rows': 3,
            }),
            'image': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:border-primary-500',
                'accept': 'image/*',
            }),
        }


class OrderItemForm(forms.Form):
    """Form for adding items to an order."""
    
    item_name = forms.CharField(
        label='اسم المادة',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200',
            'placeholder': 'أدخل اسم المادة',
            'autocomplete': 'off',
            'hx-get': '/orders/search-items/',
            'hx-trigger': 'keyup changed delay:300ms',
            'hx-target': '#item-suggestions',
        })
    )
    item_description = forms.CharField(
        label='الوصف',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200',
            'placeholder': 'وصف المادة (اختياري)',
            'rows': 2,
        })
    )
    item_image = forms.ImageField(
        label='الصورة',
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:border-primary-500',
            'accept': 'image/*',
        })
    )
    quantity = forms.IntegerField(
        label='الكمية',
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200',
            'min': '1',
        })
    )
    existing_item_id = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput()
    )


class OrderItemPriceForm(forms.Form):
    """Form for setting price on an order item (procurement committee)."""
    
    price = forms.DecimalField(
        label='السعر (دينار عراقي)',
        max_digits=15,
        decimal_places=0,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200',
            'placeholder': 'أدخل السعر',
            'min': '0',
        })
    )


class AdminReviewForm(forms.Form):
    """Form for admin review of an order item."""
    
    item_status = forms.ChoiceField(
        label='القرار',
        choices=OrderItem.ItemStatus.choices,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:border-primary-500',
        })
    )
    approved_quantity = forms.IntegerField(
        label='الكمية الموافق عليها',
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:border-primary-500',
            'min': '0',
        })
    )
    admin_note = forms.CharField(
        label='ملاحظة',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:border-primary-500',
            'placeholder': 'ملاحظة (اختياري)',
            'rows': 2,
        })
    )


