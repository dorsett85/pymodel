from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.conf import settings
from django.core.exceptions import ValidationError
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit, Field, Button

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
                Submit('register', 'Register')
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
                Submit('login', 'Login')
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
        if len(str(self.cleaned_data.get('file'))) >= 50:
            raise ValidationError({'file': 'Dataset name must be 50 characters or less'})
        return self.cleaned_data


class DatasetDescriptionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user_id = kwargs.pop('user')
        super(DatasetDescriptionForm, self).__init__(*args, **kwargs)

        self.fields['description'].widget = forms.Textarea(attrs={
            'rows': 2, 'placeholder': 'Enter dataset description'
        })
        self.fields['description'].label = 'Dataset Description'
        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.attrs = {'class': 'descripForm', 'action': '/datasetdescription'}
        self.helper.layout = Layout(
            Field('description', css_class='datasetDescripBox'),
            FormActions(
                Submit('save', 'Save', css_class='btn-sm saveDescrip'),
                Button('cancel', 'Cancel', css_class='btn-sm cancelDescrip')
            )

        )

    class Meta:
        model = Dataset
        fields = ('description',)


class CreateModelForm(forms.Form):
    dataset = forms.ChoiceField(choices=[], label='Pick a dataset')
    model_type = forms.ChoiceField(choices=(('Regression', 'Regression'), ('Classification', 'Classification')),
                                   label='What type of model?')
    pred_vars = forms.MultipleChoiceField(choices=[], label='Select predictor variables')
    resp_vars = forms.ChoiceField(choices=[], label='Select response variables')

    def __init__(self, *args, **kwargs):
        self.dataset_id = kwargs.pop('pk')
        self.user = kwargs.pop('user')
        self.user_dataset = kwargs.pop('user_dataset')
        super(CreateModelForm, self).__init__(*args, **kwargs)

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
