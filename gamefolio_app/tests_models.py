from django.test import TestCase
from django.contrib.auth.models import User
from gamefolio_app.models import Game, Review, Author, List, ListEntry


class ModelTests(TestCase):

    def setUp(self):
        # Generate generic test objects
        self.user = User.objects.create(username='testuser', email='test@example.com')
        self.author = Author.objects.create(user=self.user, website='https://www.google.com', picture='profile.jpg')
        self.author.save()

        self.game = Game.objects.create(id='test-game', title='Test Game', genre='Adventure', pictureId='abc123',
                                        description='This is a test game.')
        self.game.save()

        self.review = Review.objects.create(author=self.author, game=self.game, content='Great game!', rating=5)
        self.review.save()

        self.list = List.objects.create(author=self.author, title='Test List', description='This is a test list.')
        self.list.save()

        self.list_entry = ListEntry.objects.create(list=self.list, game=self.game)
        self.list_entry.save()



    def test_author_creation(self):
        """
        Test whether the Author model is created correctly.
        """
        self.assertEqual(self.author.user, self.user)
        self.assertEqual(self.author.website, 'https://www.google.com')
        self.assertEqual(self.author.picture, 'profile.jpg')

    def test_game_creation(self):
        """
        Test whether the Game model creates a game correctly.
        """
        game = Game.objects.get(id='test-game')
        self.assertEqual(game.title, 'Test Game')
        self.assertEqual(game.genre, 'Adventure')
        self.assertEqual(game.pictureId, 'abc123')
        self.assertEqual(game.description, 'This is a test game.')
        self.assertEqual(game.views, 0)

    def test_average_rating(self):
        """
        Test whether the average_rating method returns the correct average rating.
        """
        # Create reviews with different ratings for the game
        Review.objects.create(game=self.game, rating=4)
        Review.objects.create(game=self.game, rating=2)
        Review.objects.create(game=self.game, rating=5)

        # Calculate the expected average rating
        expected_average_rating = (4 + 2 + 5) / 3

        # Check if the calculated average rating matches the expected value
        self.assertAlmostEqual(self.game.average_rating(), expected_average_rating)

    def test_average_text_rating(self):
        """
        Test whether the average_text_rating method returns the correct text representation of the average rating.
        """
        # Create reviews with different ratings for the game
        Review.objects.create(game=self.game, rating=4)
        Review.objects.create(game=self.game, rating=2)
        Review.objects.create(game=self.game, rating=5)

        # Calculate the expected average rating
        expected_average_rating = (4 + 2 + 5) / 3

        # Check if the calculated average text rating matches the expected value
        self.assertEqual(self.game.average_text_rating(), f"{expected_average_rating:.1f} stars")

    def test_total_reviews(self):
        """
        Test whether the total_reviews method returns the correct number of reviews for the game.
        """
        # Create three reviews for the game
        Review.objects.create(game=self.game, rating=4)
        Review.objects.create(game=self.game, rating=2)
        Review.objects.create(game=self.game, rating=5)

        # Check if the total number of reviews matches the expected value
        self.assertEqual(self.game.total_reviews(), 3)

    def test_get_image(self):
        """
        Test the get_image method of the Game model.
        """
        # Test image URL retrieval
        self.assertEqual(self.game.get_image(), 'profile.jpg', )

    def test_review_creation(self):
        """
        Test whether the Review model creates a review correctly.
        """
        self.assertEqual(self.review.game, self.game)
        self.assertEqual(self.review.author, self.author)
        self.assertEqual(self.review.content, 'Great game!')
        self.assertEqual(self.review.rating, 8)
        self.assertEqual(self.review.views, 0)
        self.assertEqual(self.review.likes, 0)

    def test_list_creation(self):
        """
        Test whether the List model creates a list correctly.
        """
        self.assertEqual(self.list.author, self.author)
        self.assertEqual(self.list.title, 'Test List')
        self.assertEqual(self.list.description, 'This is a test list.')
        self.assertEqual(self.list.slug, 'test-list')  # Slug should be the same as title

    def test_list_entry_creation(self):
        """
        Test whether the ListEntry model creates a list entry correctly.
        """

        # Check if the ListEntry object is created correctly
        self.assertEqual(self.list_entry.list, self.list)
        self.assertEqual(self.list_entry.game, self.game)

    def test_str_method(self):

        #Test whether the __str__ method returns the expected string representation.

        expected_str = f"{self.user.username}'s Profile"
        self.assertEqual(str(self.author), expected_str)

        expected_str = 'Test Game'
        self.assertEqual(str(self.game), expected_str)

        expected_str = f"{self.user.username}'s Profile - Test List"
        self.assertEqual(str(self.list), expected_str)

        expected_str = f"{self.user.username} - Test Game: ★★★★★"
        self.assertEqual(str(self.review), expected_str)

    def tearDown(self):
        # delete everything once done
        self.game.delete()
        self.user.delete()
        self.author.delete()
        self.review.delete()
        self.list.delete()
        self.list_entry.delete()
