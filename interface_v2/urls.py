"""
URL configuration for interface_v2 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import *
from .initcmd import create_groups
urlpatterns = [
    path('admin/', admin.site.urls),

    # ******************************************************************************************** #
    #                            URL for users management
    # ******************************************************************************************** #
    # URL for login and logout
    path("", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    # URL where I show the home of the logged-in user
    path('home_login/', show_home_logged, name="home_login"),
    # URL for create a new base user
    path('create_user/', UserCreateView.as_view(), name="create_user"),
    # URL for create a new expert user
    path('create_expert_user/', User_expertCreateView.as_view(), name="create_expert_user"),
    # URL where I show the list of all users
    path('list_user/', UserListView.as_view(), name="list_user"),
    # URl for delete a user given the user pk
    path('delete_user/<int:user_pk>/', delete_user, name="delete_user"),
    # URL for update the user's password
    path('update_password/<int:user_pk>/', UserEditPassword.as_view(),name="update_password"),
    # URL for give a message to a user
    path('message/<str:errore>/', show_message, name="message"),

    # ******************************************************************************************** #
    #                           URLS of 'gestione' app
    # ******************************************************************************************** #
    path('gestione/', include('gestione.urls'))

]
create_groups()