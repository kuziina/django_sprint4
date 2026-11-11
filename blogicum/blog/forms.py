"""Формы приложения blog."""
from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    """Форма создания и редактирования публикации."""

    class Meta:
        """Метаданные формы PostForm."""

        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'})
        }


class CommentForm(forms.ModelForm):
    """Форма добавления и редактирования комментария."""

    class Meta:
        """Метаданные формы CommentForm."""

        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(
                attrs={'rows': 3, 'placeholder': 'Написать комментарий...'})
        }
