from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


def login_page(request):
    context = {}
    if request.user.is_authenticated:
        return redirect('main-page')
    if request.method == 'POST':
        if 'username' not in request.POST:
            context['auth_msg'] = 'Do not have a username'
        elif 'password' not in request.POST:
            context['auth_msg'] = 'Do not have a password'
        else:
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('main-page')
            else:
                context['auth_msg'] = 'Wrong credentials'
    if 'auth_msg' not in context:
        context['auth_msg'] = 'Enter your username and password'
    if request.user.is_authenticated:
        return redirect('main-page')
    return render(request, 'user/login.html', context)


@login_required(redirect_field_name='login-page')
def logout_page(request):
    logout(request)
    return redirect('login-page')
