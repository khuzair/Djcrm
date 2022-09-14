from django import forms
from django.db import models
from django.db.models import fields
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.utils.regex_helper import Choice
from .models import Lead, Agent, Category
from django.contrib.auth import get_user_model

User = get_user_model()


class LeadModelForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = (
            'first_name',
            'last_name',
            'age',
            'agent',
            'description',
            'phone_no',
            'email',
        )


class LeadForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    age = forms.IntegerField(min_value=0)


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class AssignAgentForm(forms.Form):
    # modelchoicefield takes queryset
    agent = forms.ModelChoiceField(queryset=Agent.objects.none())

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        # grab the agents for the logged in user organization
        agents = Agent.objects.filter(organization=request.user.userprofile)
        # everytime the form rendered we updating the form field
        super(AssignAgentForm, self).__init__(*args, **kwargs)
        # Display agent on a form field dynamically
        self.fields["agent"].queryset = agents


class LeadUpdateCategoryForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = (
            'category',
        )


class CategoryModelForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = (
            'name',
        )