from django import forms
from django.contrib.auth.models import User
from gamefolio_app.models import Author

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
        fields = ('website', 'picture',)
        widgets = {
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'website': 'Website',
            'picture': 'Profile Picture',
        }