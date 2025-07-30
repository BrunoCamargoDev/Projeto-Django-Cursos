# Create your views here.

from django.shortcuts import render
from enum import auto
from multiprocessing import AuthenticationError
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate, logout

# Create your views here.
def usuario_view(request):
    if request.method == 'POST': 
      user_form = UserCreationForm(request.POST)
      if user_form.is_valid():
        user_form.save()
        return redirect('login')

    else:
        user_form = UserCreationForm()


    return render (request, 'usuario.html', {'user_form': user_form})

def login_view(request):
    if request.method == 'POST':
       usuario = request.POST['username']
       senha = request.POST['password']
       user = authenticate(request, username=usuario, password=senha)
       if user is not None:
          login(request, user)
          return redirect('filmes_list')
       else:   
          login_form = AuthenticationForm()
        
    else:
       login_form = AuthenticationForm()
    return render(request, 'login.html', {'login_form': login_form})

def logout_view(request):
  logout(request)
  return redirect('filmes_list')