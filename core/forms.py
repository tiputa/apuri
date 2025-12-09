from django import forms
from .models import Room
from .models import Message
from .models import DirectMessage
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ["name", "description"]


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["text"]
        widgets = {"text": forms.Textarea(attrs={"rows": 2})}


class DirectMessageForm(forms.ModelForm):
    class Meta:
        model = DirectMessage
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 2})
        }


class JapaneseUserCreationForm(UserCreationForm):
    username = forms.CharField(
        label="ユーザー名",
        widget=forms.TextInput(attrs={'placeholder': 'ユーザー名を入力'})
    )
    password1 = forms.CharField(
        label="パスワード",
        widget=forms.PasswordInput(attrs={'placeholder': 'パスワードを入力'})
    )
    password2 = forms.CharField(
        label="パスワード（確認）",
        widget=forms.PasswordInput(attrs={'placeholder': 'もう一度パスワードを入力'})
    )

    class Meta:
        model = User
        fields = ("username",)