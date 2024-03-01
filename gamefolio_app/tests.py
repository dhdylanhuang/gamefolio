from django.test import TestCase
from django.contrib.auth.models import User
from gamefolio_app.models import Game, Review, Author

class ModelTests(TestCase):

    def setUp(self):
        #Generate generic test objects
        self.game = Game(title = "Game")
        self.game.save()
        self.user = User.objects.create_user("Mario", "mario@mario.com", "yoshi123")
        self.author = Author(user = self.user)
        self.author.save()
        
    def tearDown(self):
        #delete everything once done
        self.game.delete()
        self.user.delete()
        self.author.delete()

    #This will test that the game has a primary key that is generated as a slug
    def test_game_slug_id(self):
        gameOne = Game(title = "Test Game")
        gameOne.save()
        gameTwo = Game(title = "Test Game")
        gameTwo.save()
        self.assertEquals(gameOne.id, 'test-game')
        self.assertEqual(gameTwo.id, 'test-game-1')

    #Ensures that rating can not be above 10 or below 1
    def test_review_values(self):
        review = Review(user = self.author, game = self.game, content = "This is a random review", rating = -1)
        review.save()
        self.assertEqual(review.rating, 1)
        review = Review(user = self.author, game = self.game, content = "This is a random review", rating = 11)
        review.save()
        self.assertEqual(review.rating, 10)
