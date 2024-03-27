from django.test import TestCase
from django.contrib.auth.models import User
from gamefolio_app.models import Author
from gamefolio_app.forms import UserForm, AuthorForm

class UserFormTest(TestCase):
    def test_valid_form(self):
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword'
        }
        form = UserForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_blank_data(self):
        form = UserForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'], ['This field is required.'])
        self.assertEqual(form.errors['email'], ['This field is required.'])
        self.assertEqual(form.errors['password'], ['This field is required.'])

class AuthorFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')

    def test_valid_form(self):
        form_data = {
            'website': 'http://example.com',
        }
        form = AuthorForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_blank_data(self):
        form = AuthorForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['website'], ['This field is required.'])

    def test_valid_instance(self):
        author = Author.objects.create(user=self.user, website='http://example.com')
        form = AuthorForm(instance=author)
        self.assertTrue(form.is_valid())



