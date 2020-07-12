from django import forms
from .models import User


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'external_id',
            'username',
        )
        widgets = {
            'username': forms.TextInput,
        }
