from django import forms
from captcha.fields import ReCaptchaField
from .models import Genre, Book

class SearchForm(forms.Form):
    keyword = forms.CharField(max_length=20, label='Поиск', required=False)
    genre = forms.ModelChoiceField(queryset=Genre.objects.all(), label='Жанр')

class BookForm(forms.ModelForm):
    captcha = ReCaptchaField(label='Введите текст с картинки', error_messages={'invalid': 'Неправильный текст'})

    class Meta:
        model = Book
        fields = ('name', 'description', 'author', 'genre', 'published_date', 'captcha')
