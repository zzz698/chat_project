from django import forms
from .models import Message, GlobalBackground


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text', 'image']

class BackgroundImageForm(forms.ModelForm):
    class Meta:
        model = GlobalBackground
        fields = ['image']
# 开发者：zxb
# 开发时间：2025/5/21 下午2:39
from django import forms
from django.contrib.auth.models import User
from .models import Profile

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']

