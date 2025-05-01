from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Post, DiscussionPost
from .models import Poll, Poll_Comment
from .models import Album, DiscussionTopic


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


class DiscussionPostForm(forms.ModelForm):
    class Meta:
        model = DiscussionPost
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control','placeholder': 'Title...'}),
            'content': forms.Textarea(attrs={'class':'form-control','placeholder': 'Enter text here...'}),
        }


class DiscussionTopicForm(forms.ModelForm):
    class Meta:
        model = DiscussionTopic
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'New topic title…',
                'class': 'form-control',
            }),
        }


class PollForm(forms.ModelForm):
    class Meta:
        model = Poll
        fields = ['question']
        widgets = {
            'question': forms.TextInput(attrs={'placeholder': 'Enter your poll question here'}),
        }


class PollCommentForm(forms.ModelForm):
    class Meta:
        model = Poll_Comment
        fields = ['comment_text']
        widgets = {
            'comment_text': forms.Textarea(attrs={
                'placeholder': 'Type your comment here...',
                'rows': 4,
                'cols': 2
            })
        }


class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Album title…',
                'class': 'form-control',
            }),
        }
