from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from .models import *

class InsertQuestionForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_id = "insert_question_form"
    helper.form_method = "POST"
    helper.add_input(Submit('submit', 'submit'))

    class Meta:
        model = Question
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'class': 'my-custom-textarea'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
