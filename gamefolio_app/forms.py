from django import forms
from django.contrib.auth.models import User
from gamefolio_app.models import Author, List, Game, Review, ListEntry

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password',)
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'username': 'Username',
            'email': 'Email',
            'password': 'Password',
        }
        
    def clean(self):
        cleaned_data = self.cleaned_data
        url = cleaned_data.get('url')

        if url and not url.startswith('http://'):
            url = f'http://{url}'
            cleaned_data['url'] = url
        
        return cleaned_data

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ('website', 'picture', 'bio',)
        widgets = {
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': '5', 'maxlength': '200'}),
        }
        labels = {
            'website': 'Website',
            'picture': 'Profile Picture',
            'bio': 'Bio',
        }
        
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'content']
        widgets = {
            'rating': forms.Select(choices=Review.RATING_CHOICES, attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, "maxlength": 500}),
        }
        labels = {
            'rating': 'Rating',
            'content': 'Review Content',
        }

class CreateListForm(forms.ModelForm):
    games = forms.ModelMultipleChoiceField(queryset=Game.objects.all().order_by('title'), widget=forms.CheckboxSelectMultiple, required = False)

    class Meta:
        model = List
        fields = ['title', 'description', 'games']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', "maxlength": 500}),
        }
        labels = {
            'title': 'Title',
            'description': 'Description',
            'games': 'Games',
        }

