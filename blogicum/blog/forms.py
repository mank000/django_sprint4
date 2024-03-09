from django import forms

from .models import Comment, Post


class CreatePostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author', )
        widgets = {
            'pub_date': forms.DateTimeInput(format='%Y-%m-%d %H:%M:%S',
                                            attrs={'type': 'datetime-local'})
        }


class CommentsForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
