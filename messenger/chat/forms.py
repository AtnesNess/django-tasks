from django import forms
from django.contrib.auth.forms import  AuthenticationForm
from chat.models import ChatUser
from django.contrib import auth
from django.core.files import File

from chat.models import ChatUser


class RegistrationForm(forms.ModelForm):
    """
    Form for registering a new account.
    """
    username = forms.CharField(widget=forms.widgets.TextInput, label="Username")
    password1 = forms.CharField(widget=forms.widgets.PasswordInput,
                                label="Password")
    password2 = forms.CharField(widget=forms.widgets.PasswordInput,
                                label="Password (again)")

    class Meta:
        model = ChatUser
        fields = ['username', 'password1', 'password2']

    def clean(self):
        """
        Verifies that the values entered into the password fields match

        NOTE: Errors here will appear in ``non_field_errors()`` because it applies to more than one field.
        """
        cleaned_data = super(RegistrationForm, self).clean()
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError("Passwords don't match. Please enter both fields again.")
        return self.cleaned_data

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class InfoForm(forms.Form):
    avatar = forms.ImageField(label='avatar', required=False)
    status = forms.CharField(label='status', required=False)



