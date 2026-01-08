from django import forms


class PriceItemForm(forms.Form):
    """Form for pricing an order item."""
    
    price = forms.DecimalField(
        max_digits=15,
        decimal_places=0,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200',
            'placeholder': 'السعر',
            'min': '0',
        })
    )


class AdminDecisionForm(forms.Form):
    """Form for admin decision on an order item."""
    
    DECISION_CHOICES = [
        ('approved', 'موافق'),
        ('declined', 'مرفوض'),
        ('modified', 'معدل'),
    ]
    
    decision = forms.ChoiceField(
        choices=DECISION_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'accent-primary-600',
        })
    )
    approved_quantity = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:border-primary-500',
            'placeholder': 'الكمية الموافق عليها',
            'min': '0',
        })
    )
    admin_note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:border-primary-500',
            'placeholder': 'ملاحظة (اختياري)',
            'rows': 2,
        })
    )


class BulkDecisionForm(forms.Form):
    """Form for bulk admin decision."""
    
    BULK_CHOICES = [
        ('approve_all', 'الموافقة على الجميع'),
        ('decline_all', 'رفض الجميع'),
    ]
    
    bulk_action = forms.ChoiceField(
        choices=BULK_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'accent-primary-600',
        })
    )
    admin_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 focus:border-primary-500',
            'placeholder': 'ملاحظات عامة (اختياري)',
            'rows': 3,
        })
    )


