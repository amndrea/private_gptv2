from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

"""
class InserisciDomandaForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_id = "insert_dieta_crispy_form"
    helper.form_method = "POST"
    helper.add_input(Submit('submit', 'submit'))

    class Meta:
        model = Domanda
        fields = ['commento']
        widgets = {
            'commento': forms.Textarea(attrs={'class': 'my-custom-textarea'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
"""