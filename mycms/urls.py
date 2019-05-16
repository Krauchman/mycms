"""mycms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from contest import views as contest_views
from user import views as user_views
import nested_admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('contest/', include('contest.urls')),
    path('accounts/login/', user_views.login_page, name='login-page'),
    path('logout/', user_views.logout_page, name='logout-page'),
    path('', contest_views.contest_list, name='main-page'),

    path('nested-admin/', include('nested_admin.urls')),
]
