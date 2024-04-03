from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Post


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['caption', 'image']
        widgets = {
            'caption': forms.TextInput(attrs={'placeholder': 'Write your caption here...',
                                              'style': 'min-height: 200px; padding: 10px; border-radius: 25px; resize: vertical; line-height: 1.5;',
                                              },
                                       ),
        }
