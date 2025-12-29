from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistroClienteForm


def home(request):
    """Vista principal de la tienda."""
    return render(request, 'home.html')


def registro(request):
    """Vista de registro para nuevos clientes."""
    if request.method == 'POST':
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, '¡Cuenta creada exitosamente! Ya puedes iniciar sesión.')
            return redirect('login')
    else:
        form = RegistroClienteForm()
    return render(request, 'usuarios/registro.html', {'form': form})


@login_required
def perfil(request):
    """Vista del perfil del usuario."""
    return render(request, 'usuarios/perfil.html', {'usuario': request.user})
