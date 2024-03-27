from django.test import TestCase
from gamefolio_app.models import Game, Author, Review, List, ListEntry
from django.contrib.auth.models import User
from populate_gamefolio import *


class PopulationScriptTests(TestCase):
    """
    Tests for the populate_gamefolio.py script.
    """

    def setUp(self):
        """
        Set up the environment for testing.
        """
        # Populate the database with sample data
        populate_games()
        populate_users()
        populate_reviews()
        populate_lists()

        total_games = Game.objects.count()
        avg_reviews_per_game = AVG_REVIEWS_PER_GAME
        total_users = NUMBER_OF_USERS
        user_with_list_percent = USER_WITH_LIST_PERCENT
        avg_list_entry_per_list = 10

        self.expected_review_count = total_games * avg_reviews_per_game
        self.expected_list_count = total_users * user_with_list_percent
        self.expected_list_entry_count = self.expected_list_count * avg_list_entry_per_list

    def test_game_population(self):
        """
        Test if games are populated correctly.
        """
        # Check if the total number of games matches the expected value
        self.assertEqual(Game.objects.count(), NUMBER_OF_GAMES)

        # Get a sample game
        sample_game = Game.objects.first()

        # Check if the title is not empty
        self.assertNotEqual(sample_game.title, "")

        # Check if the genre is valid (if applicable)
        if sample_game.genre:
            self.assertTrue(sample_game.genre in ["Action", "Adventure", "RPG", "Strategy"])

        # Check if the description is not empty
        self.assertNotEqual(sample_game.description, "")

        # Check if the picture ID is not empty
        self.assertNotEqual(sample_game.pictureId, "")


    def test_user_population(self):
        """
        Test if users are populated correctly.
        """
        # Check if the total number of users matches the expected value
        self.assertEqual(User.objects.count(), NUMBER_OF_USERS)

        # Get a sample user
        sample_user = User.objects.first()

        # Check if the username is not empty
        self.assertNotEqual(sample_user.username, "")

        # Check if the email is valid
        self.assertTrue('@' in sample_user.email)

        # Check if the author profile is created for the user
        self.assertTrue(hasattr(sample_user, 'author'))

    def test_review_population(self):
        """
        Test if reviews are populated correctly.
        """
        # Check if the total number of reviews matches the expected value
        self.assertEqual(Review.objects.count(), self.expected_review_count)

        # Get a sample review
        sample_review = Review.objects.first()

        # Check if the content is not empty
        self.assertNotEqual(sample_review.content, "")

        # Check if the rating is within the valid range
        self.assertTrue(1 <= sample_review.rating <= 10)

        # Check if the likes are non-negative
        self.assertTrue(sample_review.likes >= 0)

    def test_list_population(self):
        """
        Test if lists and list entries are populated correctly.
        """
        # Check if the total number of lists matches the expected value
        self.assertEqual(List.objects.count(), self.expected_list_count)

        # Check if the total number of list entries matches the expected value
        self.assertEqual(ListEntry.objects.count(), self.expected_list_entry_count)

        # Get a sample list and list entry
        sample_list = List.objects.first()
        sample_list_entry = ListEntry.objects.first()

        # Check if the list title is not empty
        self.assertNotEqual(sample_list.title, "")

        # Check if the list description is not empty
        self.assertNotEqual(sample_list.description, "")

        # Check if the list entry is associated with a valid list and game
        self.assertTrue(hasattr(sample_list_entry, 'list'))
        self.assertTrue(hasattr(sample_list_entry, 'game'))


    def tearDown(self):
        """
        Clean up after testing.
        """
        # Clear the database
        clear_database()

