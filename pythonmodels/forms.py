from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.conf import settings
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit

from .models import Dataset

import os


class RegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            'username',
            'password1',
            'password2',
            ButtonHolder(
                Submit('register', 'Register', css_class='btn-primary')
            )
        )


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            'username',
            'password',
            ButtonHolder(
                Submit('login', 'Login', css_class='btn-primary')
            )
        )


class DatasetForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DatasetForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.attrs = {'id': 'uploadData', 'class': 'dropzone'}
        self.helper.layout = Layout(
            # 'file',
            'description',
            # ButtonHolder(
            #     Submit('dataUpload', 'Submit', css_class='btn-primary')
            # )
        )

    class Meta:
        model = Dataset
        fields = ('file', 'description',)

    def clean(self):
        file_path = settings.MEDIA_ROOT + '/user_{0}/'.format(1) + str(self.cleaned_data.get('file'))
        print(self.fields)
        if os.path.isfile(file_path):
            raise ValidationError('File already exists')
        return self.cleaned_data
