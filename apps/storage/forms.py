from django import forms
from django.db.models import Q
from .models import StorageItem
from apps.departments.models import Department, Branch


class StorageItemForm(forms.ModelForm):
    """Form for creating and editing storage items."""
    
    branch = forms.ModelChoiceField(
        queryset=Branch.objects.none(),  # Will be set in __init__
        label='الفرع',
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200'
        })
    )
    
    department = forms.ModelChoiceField(
        queryset=Department.objects.none(),  # Will be set in __init__
        label='الشعبة',
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200'
        })
    )
    
    class Meta:
        model = StorageItem
        fields = ['name', 'description', 'quantity', 'branch', 'department']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200',
                'placeholder': 'اسم المادة'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200',
                'rows': 3,
                'placeholder': 'وصف المادة (اختياري)'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200',
                'min': 0,
                'placeholder': 'الكمية'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Always load all branches
        self.fields['branch'].queryset = Branch.objects.all()
        
        # Load all departments initially
        self.fields['department'].queryset = Department.objects.all()
        
        # If editing and instance has a branch, filter departments by that branch
        # Include departments that belong to this branch OR have no branch assigned
        if self.instance and self.instance.pk and self.instance.branch:
            self.fields['department'].queryset = Department.objects.filter(
                Q(branch=self.instance.branch) | Q(branch__isnull=True)
            )

