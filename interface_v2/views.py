from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, ListView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.urls import reverse_lazy
from .forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import user_passes_test
from django.contrib import messages


# ---------------------------------------------------------------------------------------------#
# View showing the home of a logged in user
# ---------------------------------------------------------------------------------------------#
def show_home_logged(request):
    return render(request, template_name="home_login.html")



# ******************************************************************************************** #
#                         Views for the users management
# ******************************************************************************************** #
# -------------------------------------------------------------------------------------------- #
# Class for creating base user or expert users
# ---------------------------------------------------------------------------------------------#
class UserCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "is_staff"
    template_name = "users/create_user.html"
    form_class = FormCreateUser

    def get_success_url(self):
        return reverse_lazy("list_user")


class User_expertCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "is_staff"
    template_name = "users/create_user.html"
    form_class = FormCreeateExpertUser
    def get_success_url(self):
        return reverse_lazy("list_user")


# ---------------------------------------------------------------------------------------------#
# Class to display all users who are not the admin
# ---------------------------------------------------------------------------------------------#
class UserListView(PermissionRequiredMixin, ListView):
    permission_required = "is_staff"
    model = User
    template_name = "users/list_users.html"
    context_object_name = "users"

    def get_queryset(self):
        queryset = User.objects.exclude(is_superuser=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        numero_utenti = User.objects.count()
        context['num_utenti'] = numero_utenti
        return context


# ------------------------------------------------------------------------ #
# Class to update a user's password
# ------------------------------------------------------------------------ #
class UserEditPassword(LoginRequiredMixin, FormView):
    template_name = "users/update_password.html"
    form_class = UpdatePasswordForm
    success_url = reverse_lazy("message")

    def get_context_data(self, **kwargs):
        user = User.objects.get(pk=self.kwargs.get('user_pk'))
        context = super().get_context_data(**kwargs)
        context['user'] = user
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = get_object_or_404(User, pk=self.kwargs['user_pk'])
        return kwargs

    def form_valid(self, form):
        user = form.save(commit=False)
        new_password1 = form.cleaned_data.get("new_password1")
        new_password2 = form.cleaned_data.get("new_password2")
        print(new_password1)
        print(new_password2)
        if new_password1 == new_password2:
            user.set_password(form.cleaned_data['new_password1'])
            user.save()
            return redirect('message',"0")
        else:
            return redirect('message',"1")


# ------------------------------------------------------------------------ #
# Function for show a message for user
# ------------------------------------------------------------------------ #
def show_message (request, errore):
    context = {"errore": errore}
    return render(request,  template_name="users/message.html", context=context)


# ------------------------------------------------------------------------ #
# Function for delete a user given the primary key
# ------------------------------------------------------------------------ #
@login_required
@user_passes_test(lambda u: u.is_staff)
def delete_user(request, user_pk):
    user_to_delete = get_object_or_404(User, id=user_pk)
    if request.method == 'POST':
        if user_to_delete == request.user:
            messages.error(request, "Non puoi cancellare te stesso.")
            return redirect('list_user')
        user_to_delete.delete()
        messages.success(request, f"L'utente {user_to_delete.username} è stato cancellato con successo.")
        return redirect('list_user')
    context = {'user_to_delete': user_to_delete}
    return render(request, 'users/delete_user.html', context)