from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

def index(request):
    if request.user.is_authenticated:
        return redirect('Admin:inicio')  # Puedes cambiar 'dashboard' por el nombre real

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        usuario = authenticate(request, email=email, password=password)

        if usuario is not None:
            login(request, usuario)
            return redirect('Admin:inicio')  # Siempre va al mismo lugar
        else:
            messages.error(request, 'Correo o contraseña incorrectos.')

    return render(request, 'auth/index.html')
