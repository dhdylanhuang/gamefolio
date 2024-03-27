import os
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.text import slugify

#from gamefolio_app.forms import CreateListForm
from gamefolio_app.models import Game, Review, Author, List, ListEntry
from gamefolio_app.views import MyRegistrationView
from populate_gamefolio import populate, clear_database


FAILURE_HEADER = f"{os.linesep}{os.linesep}{os.linesep}================{os.linesep}TwD TEST FAILURE =({os.linesep}================{os.linesep}"
FAILURE_FOOTER = f"{os.linesep}"

class IndexViewTests(TestCase):
    def setUp(self):
        self.response = self.client.get(reverse('gamefolio_app:index'))
        self.content = self.response.content.decode()

    def test_template_filename(self):
        self.assertTemplateUsed(self.response, 'gamefolio_app/index.html', f"{FAILURE_HEADER}Are you using index.html for your index() view? Why not?!{FAILURE_FOOTER}")

    def test_index_view(self):
        # Test index view
        response = self.client.get(reverse('gamefolio_app:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gamefolio_app/index.html')

        # Check if game list and reviews list are in the context
        self.assertIn('games', response.context)
        self.assertIn('reviews', response.context)

        # Check if the context lists are not empty
        self.assertTrue(len(response.context['games']) > 0)
        self.assertTrue(len(response.context['reviews']) > 0)

        # Check if game list and reviews list are instances of QuerySet
        self.assertIsInstance(response.context['games'], Game.objects.all().__class__)
        self.assertIsInstance(response.context['reviews'], Review.objects.all().__class__)


    def tearDown(self):
        clear_database()

class MyRegistrationViewTests(TestCase):
    def setUp(self):
        self.registration_view = MyRegistrationView()

    def test_get_success_url(self):
        # Test if the get_success_url method returns the correct success URL
        success_url = self.registration_view.get_success_url()
        expected_url = reverse('gamefolio_app:register_profile')
        self.assertEqual(success_url, expected_url, "The success URL returned by get_success_url method is incorrect.")

class RegisterProfileViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')

    def test_get(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('gamefolio_app:register_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gamefolio_app/profile_registration.html')

    def test_post_valid_form(self):
        self.client.force_login(self.user)
        data = {
            'field1': 'value1',
            'field2': 'value2',
            # Add other fields as needed
        }
        response = self.client.post(reverse('gamefolio_app:register_profile'), data)
        self.assertEqual(response.status_code, 302)  # Check if redirected after successful form submission
        self.assertEqual(response.url, reverse('gamefolio_app:index'))  # Check if redirected to the correct URL

    def test_post_invalid_form(self):
        self.client.force_login(self.user)
        data = {}  # Invalid data, form should fail validation
        response = self.client.post(reverse('gamefolio_app:register_profile'), data)
        self.assertEqual(response.status_code, 200)  # Form submission should return to the same page
        self.assertTemplateUsed(response, 'gamefolio_app/profile_registration.html')  # Check if correct template is used
        # Add more assertions if needed to test form errors or other behavior


class UserLoginViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')

    def test_get(self):
        response = self.client.get(reverse('gamefolio_app:user_login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gamefolio_app/registration/login.html')

    def test_post_valid_credentials(self):
        data = {
            'username': 'testuser',
            'password': 'testpassword',
        }
        response = self.client.post(reverse('gamefolio_app:user_login'), data)
        self.assertEqual(response.status_code, 302)  # Check if redirected after successful login
        self.assertEqual(response.url, reverse('gamefolio_app:profile'))  # Check if redirected to the correct URL

    def test_post_invalid_credentials(self):
        data = {
            'username': 'invaliduser',
            'password': 'invalidpassword',
        }
        response = self.client.post(reverse('gamefolio_app:user_login'), data)
        self.assertEqual(response.status_code, 200)  # Login attempt should return to the same page
        self.assertTemplateUsed(response, 'gamefolio_app/registration/login.html')  # Check if correct template is used

class UserLogoutViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_logout(self):
        response = self.client.get(reverse('gamefolio_app:user_logout'))
        self.assertEqual(response.status_code, 302)  # Check if redirected after logout
        self.assertEqual(response.url, reverse('gamefolio_app:index'))  # Check if redirected to the correct URL
        self.assertFalse('_auth_user_id' in self.client.session)  # Check if user is logged out

    def test_logout_redirect(self):
        response = self.client.get(reverse('gamefolio_app:user_logout') + '?next=/some/other/url/')
        self.assertEqual(response.status_code, 302)  # Check if redirected after logout
        self.assertEqual(response.url, '/some/other/url/')  # Check if redirected to the correct URL
        self.assertFalse('_auth_user_id' in self.client.session)  # Check if user is logged out

class ProfileViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.author = Author.objects.create(user=self.user, website='http://example.com')
        self.review = Review.objects.create(author=self.author, content='Test review')
        self.profile_url = reverse('gamefolio_app:profile', kwargs={'username': self.user.username})

    def test_get_profile_view(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gamefolio_app/profile.html')

    def test_post_profile_view(self):
        # Prepare POST data
        post_data = {
            'website': 'http://updated-example.com',
            'picture': SimpleUploadedFile('test_image.jpg', b'content', content_type='image/jpeg')
        }
        response = self.client.post(self.profile_url, post_data)
        self.assertEqual(response.status_code, 302)  # Check if redirected after form submission
        updated_author = Author.objects.get(user=self.user)
        self.assertEqual(updated_author.website, 'http://updated-example.com')  # Check if website is updated
        self.assertTrue(updated_author.picture)  # Check if picture is uploaded

    def test_unauthorised_access(self):
        another_user = User.objects.create_user(username='anotheruser', email='another@example.com', password='anotherpassword')
        response = self.client.get(reverse('gamefolio_app:profile', kwargs={'username': another_user.username}))
        self.assertEqual(response.status_code, 403)  # Check if access is forbidden for other users

class ListProfilesViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.author1 = Author.objects.create(user=self.user)
        self.author2 = Author.objects.create(user=User.objects.create_user(username='testuser2', email='test2@example.com', password='testpassword'))
        self.review1 = Review.objects.create(author=self.author1, content='Test review 1', likes=10)
        self.review2 = Review.objects.create(author=self.author1, content='Test review 2', likes=5)
        self.review3 = Review.objects.create(author=self.author2, content='Test review 3', likes=15)

    def test_list_profiles_view_sort_by_reviews(self):
        response = self.client.get(reverse('gamefolio_app:list_profiles'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gamefolio_app/list_profiles.html')
        authors = response.context['authors']
        self.assertEqual(len(authors), 2)
        self.assertEqual(authors[0].total_reviews, 2)
        self.assertEqual(authors[1].total_reviews, 1)

    def test_list_profiles_view_sort_by_likes(self):
        response = self.client.get(reverse('gamefolio_app:list_profiles'), {'sort_by': 'likes'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gamefolio_app/list_profiles.html')
        authors = response.context['authors']
        self.assertEqual(len(authors), 2)
        self.assertEqual(authors[0].total_likes, 15)
        self.assertEqual(authors[1].total_likes, 15)

class ListViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.list_author = User.objects.create_user(username='list_author', email='author@example.com', password='authorpassword')
        self.list = List.objects.create(title='Test List', author=self.list_author.profile)
        self.game = Game.objects.create(title='Test Game')
        self.list_entry = ListEntry.objects.create(list=self.list, game=self.game)
        self.list_url = reverse('gamefolio_app:list', kwargs={'author_username': self.list_author.username, 'list_title': slugify(self.list.title), 'slug': self.list.slug})

    def test_get_list_view(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gamefolio_app/list.html')
        self.assertIn(self.list, response.context['list_obj'])
        self.assertIn(self.list_entry, response.context['list_entries'])
        self.assertIn(self.game, response.context['all_games'])

    def test_post_list_view(self):
        post_data = {'game': self.game.id}
        response = self.client.post(self.list_url, post_data)
        self.assertEqual(response.status_code, 302)  # Check if redirected after adding game
        updated_list_entries = ListEntry.objects.filter(list=self.list)
        self.assertTrue(updated_list_entries.exists())  # Check if list entry is created
        self.assertEqual(updated_list_entries.count(), 2)  # Check if the number of list entries increased

class ListsViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_get_lists_view(self):
        response = self.client.get(reverse('gamefolio_app:lists'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gamefolio_app/lists.html')
        #self.assertIsInstance(response.context['create_list_form'], CreateListForm)
        self.assertQuerysetEqual(response.context['all_lists'], [])
        self.assertQuerysetEqual(response.context['user_list'], [])

    def test_post_lists_view(self):
        post_data = {
            'title': 'Test List',
            'description': 'Test description',
            'games': [],
        }
        response = self.client.post(reverse('gamefolio_app:lists'), post_data)
        self.assertEqual(response.status_code, 302)  # Check if redirected after form submission
        new_list = List.objects.first()
        self.assertIsNotNone(new_list)  # Check if the new list is created
        self.assertEqual(new_list.author, self.user.profile)  # Check if the author is set correctly
        self.assertEqual(new_list.title, 'Test List')  # Check if the title is set correctly
        self.assertEqual(new_list.description, 'Test description')  # Check if the description is set correctly
        self.assertQuerysetEqual(new_list.games.all(), [])  # Check if no games are added to the list initially

class NotFoundViewTests(TestCase):
    def test_get_not_found_view(self):
        response = self.client.get(reverse('gamefolio_app:not_found'))
        self.assertEqual(response.status_code, 200)  # Ensure the status code is correct
        self.assertTemplateUsed(response, 'gamefolio_app/404.html')  # Ensure the correct template is used

class SearchViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')

    def test_search_view_no_params(self):
        response = self.client.get(reverse('gamefolio_app:search'))
        self.assertEqual(response.status_code, 200)  # Ensure the status code is correct
        self.assertTemplateUsed(response, 'gamefolio_app/search.html')  # Ensure the correct template is used

    def test_search_view_with_query(self):
        response = self.client.get(reverse('gamefolio_app:search'), {'query': 'test'})
        self.assertEqual(response.status_code, 200)  # Ensure the status code is correct
        self.assertTemplateUsed(response, 'gamefolio_app/search.html')  # Ensure the correct template is used

    def test_search_view_with_params(self):
        response = self.client.get(reverse('gamefolio_app:search'), {'query': 'test', 'page': 1, 'genre': 'Action', 'sort': 'rd'})
        self.assertEqual(response.status_code, 200)  # Ensure the status code is correct
        self.assertTemplateUsed(response, 'gamefolio_app/search.html')  # Ensure the correct template is used

    def test_search_view_different_sorting(self):
        # Test with different sorting options
        sorting_options = ['rd', 'ra', 'vd', 'va', 'ta', 'td']
        for sort_option in sorting_options:
            response = self.client.get(reverse('gamefolio_app:search'), {'query': 'test', 'sort': sort_option})
            self.assertEqual(response.status_code, 200)  # Ensure the status code is correct
            self.assertTemplateUsed(response, 'gamefolio_app/search.html')  # Ensure the correct template is used

    def test_search_view_different_page(self):
        response = self.client.get(reverse('gamefolio_app:search'), {'query': 'test', 'page': 2})
        self.assertEqual(response.status_code, 200)  # Ensure the status code is correct
        self.assertTemplateUsed(response, 'gamefolio_app/search.html')  # Ensure the correct template is used

class RemoveGameViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.game = Game.objects.create(title='Test Game')
        self.list = List.objects.create(title='Test List', author=self.user.profile)
        self.list_entry = ListEntry.objects.create(list=self.list, game=self.game)

    def test_remove_game(self):
        response = self.client.post(reverse('gamefolio_app:remove_game', kwargs={'list_id': self.list.id, 'game_id': self.game.id}))
        self.assertEqual(response.status_code, 302)  # Check if redirected after removing game
        self.assertFalse(ListEntry.objects.filter(list=self.list, game=self.game).exists())  # Check if the game is removed from the list

class CreateListViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_create_list(self):
        response = self.client.post(reverse('gamefolio_app:create_list'), {'title': 'New List', 'description': 'Description'})
        self.assertEqual(response.status_code, 302)  # Check if redirected after creating list
        self.assertTrue(List.objects.filter(title='New List', author=self.user.profile).exists())  # Check if the new list is created

class ListDeleteViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.list = List.objects.create(title='Test List', author=self.user.profile)

    def test_delete_list(self):
        response = self.client.post(reverse('gamefolio_app:list_delete', kwargs={'pk': self.list.pk}))
        self.assertEqual(response.status_code, 302)  # Check if redirected after deleting list
        self.assertFalse(List.objects.filter(pk=self.list.pk).exists())  # Check if the list is deleted

class GamePageViewTests(TestCase):
    def setUp(self):
        self.game = Game.objects.create(title='Test Game')

    def test_game_page_view(self):
        response = self.client.get(reverse('gamefolio_app:game_page', kwargs={'slug': self.game.slug}))
        self.assertEqual(response.status_code, 200)  # Check if the game page is accessible
        self.assertTemplateUsed(response, 'gamefolio_app/game_page.html')  # Check if the correct template is used
