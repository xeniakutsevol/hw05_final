from xml.etree.ElementTree import Comment
from django import forms
from .models import Post, Comment
from django.utils.translation import gettext_lazy as _


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        help_texts = {
            'text': _('Добавьте текст поста (обязательно).'),
            'group': _('Добавьте сообщество (необязательно).'),
            'image': _('Добавьте изображение (необязательно).'),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        help_texts = {
            'text': _('Добавьте комментарий.')
        }
