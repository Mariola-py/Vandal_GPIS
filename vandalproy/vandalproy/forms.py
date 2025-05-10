from django import forms
from .models import BlogComment

class CommentForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Escribe tu comentario aquí...'
        }),
        label=''
    )

    class Meta:
        model = BlogComment
        fields = ['content']