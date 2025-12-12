from django import forms
from .models import Room
from .models import Message
from .models import DirectMessage
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


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
        fields = ["text"]
        widgets = {"text": forms.Textarea(attrs={"rows": 2})}


class JapaneseUserCreationForm(UserCreationForm):
    username = forms.CharField(
        label="ユーザー名",
        widget=forms.TextInput(attrs={"placeholder": "ユーザー名を入力"}),
    )
    password1 = forms.CharField(
        label="パスワード",
        widget=forms.PasswordInput(attrs={"placeholder": "パスワードを入力"}),
    )
    password2 = forms.CharField(
        label="パスワード（確認）",
        widget=forms.PasswordInput(attrs={"placeholder": "もう一度パスワードを入力"}),
    )

    class Meta:
        model = User
        fields = ("username",)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["bio", "profile_image"]

        labels = {
            "bio": "一言",
            "profile_image": "プロフィール画像",
        }

        widgets = {
            # 一言（1行入力）
            "bio": forms.TextInput(
                attrs={
                    "placeholder": "ひとこと入力",
                    "maxlength": "50",
                    "style": """
                        width:100%;
                        padding:10px;
                        font-size:14px;
                        border-radius:8px;
                        border:1px solid #ccc;
                    """,
                }
            ),

            # 画像アップロード
            "profile_image": forms.ClearableFileInput(
                attrs={
                    "style": "margin-top:8px;",
                }
            ),
        }