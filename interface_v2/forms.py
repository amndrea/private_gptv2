from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth.forms import PasswordChangeForm

# ----------------------------------------------------------------------------------------#
# Form to create a user and insert it into the group 'base_user'
# ----------------------------------------------------------------------------------------#
class FormCreateUser(UserCreationForm):
    helper = FormHelper()
    helper.form_id = "crea_utente_form"
    helper.form_method = "POST"
    helper.add_input(Submit('submit', 'submit'))

    class Meta:
        model = User
        exclude = ['password', 'last_login', 'is_superuser', 'groups', 'user_permissions', 'is_staff', 'is_active',
                   'date_joined']

    def save(self, commit=True):
        user = super().save(commit)
        g = Group.objects.get(name="base_user")
        g.user_set.add(user)
        return user


# ----------------------------------------------------------------------------------------#
# Form to create a user and insert it into the group 'base_user'
# ----------------------------------------------------------------------------------------#
class UpdatePasswordForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_id = "edit_user_password"
    helper.form_method = 'POST'
    helper.add_input(Submit('submit', 'submit'))

    new_password1 = forms.CharField(widget=forms.PasswordInput)
    new_password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['new_password1', 'new_password2']