from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.conf import settings
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit, Field

from .models import Dataset, DatasetVariable

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


class DatasetUploadForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user_id = kwargs.pop('user')
        super(DatasetUploadForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.attrs = {'id': 'uploadData', 'class': 'dropzone'}
        self.helper.layout = Layout(
            Field(
                'description', type="hidden"
            ),
            # 'description',
        )

    class Meta:
        model = Dataset
        fields = ('file', 'description',)

    def clean(self):
        file_path = settings.MEDIA_ROOT + '/user_{0}/'.format(self.user_id) + str(self.cleaned_data.get('file'))
        if os.path.isfile(file_path):
            raise ValidationError({'file': 'File already exists!'})
        return self.cleaned_data


class CreateModel(forms.Form):
    dataset = forms.ChoiceField(choices=[], label='Pick a dataset')
    model_type = forms.ChoiceField(choices=(('Regression', 'Regression'), ('Classification', 'Classification')),
                                   label='What type of model?')
    pred_vars = forms.MultipleChoiceField(choices=[], label='Select predictor variables')
    resp_vars = forms.ChoiceField(choices=[], label='Select response variables')

    def __init__(self, *args, **kwargs):
        self.dataset_id = kwargs.pop('pk')
        self.user = kwargs.pop('user')
        self.user_dataset = kwargs.pop('user_dataset')
        super(CreateModel, self).__init__(*args, **kwargs)

        # Add field values
        dataset_choices = [dat for dat in self.user_dataset] if self.user_dataset else [(1, 'No datasets uploaded')]
        self.fields['dataset'].choices = [
            ("{0}'s Datasets".format(self.user), dataset_choices),
            ("Public", [dat for dat in self.user_dataset])
        ]
        self.helper = FormHelper()
        self.helper.attrs = {'id': 'modelCreateForm'}
        self.helper.layout = Layout(
            Field(
                'dataset', id="dataID", name='dataID'
            ),
        )
