from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class RegistroClienteForm(UserCreationForm):
    """Formulario de registro para clientes."""
    
    email = forms.EmailField(required=True)
    cedula = forms.CharField(max_length=20, required=True, label='Cédula')
    celular = forms.CharField(max_length=15, required=True, label='Celular')
    direccion = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=True, label='Dirección')
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'cedula', 'celular', 'direccion', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.rol = CustomUser.Rol.CLIENTE
        user.email = self.cleaned_data['email']
        user.cedula = self.cleaned_data['cedula']
        user.celular = self.cleaned_data['celular']
        user.direccion = self.cleaned_data['direccion']
        if commit:
            user.save()
        return user
