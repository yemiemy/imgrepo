from django import forms
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()

class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=30, label='First name', required=True)
    last_name = forms.CharField(max_length=30, label='Last name', required=True)
    seller = forms.BooleanField(required=False, label='Join as a seller')
    customer = forms.BooleanField(required=False, label='Join as a buyer')

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.seller = self.cleaned_data['seller']
        user.customer = self.cleaned_data['customer']
        user.save()
        
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'image',
            'phone',
            'business_name',
            'acc_number',
            'bank_name',
            'facebook',
            'instagram',
            'twitter']

choices = [
    ('','(select experience)'),
    ('novice','I take some nice pictures'),
    ('professional','I am a professional'),
    ('expert','I am an expert in photography')
]

class BecomeSeller(forms.Form):
    business_name = forms.CharField(max_length=30, label='Business Name', required=True)
    experience = forms.CharField(max_length=30, label='Experience Level', required=True, widget=forms.Select(choices=choices))
    # photgrapher = forms.BooleanField(required=False, label='Join as a seller')
    # customer = forms.BooleanField(required=False, label='Join as a buyer')
