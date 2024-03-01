import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','gamefolio.settings')
import django
django.setup()

import requests
from numpy import random
from datetime import datetime, timedelta

from gamefolio_app.models import Author, Game, Review, List, ListEntry
from django.contrib.auth.models import User

###########################################################- Parameters and Constants -###########################################################

### General Parameters ###
SEED = 42

### Game Parameters ###
#Secret API Key stuff, only reason its here is cos the repo is private
CLIENT_ID = "2w3wcvvgqis5plpiqbhxh7cud3szm0"
BEARER = "5obg1bjuw5aniisksxd401n5sbca2f"
BASE_REQUEST = {'headers': {'Client-ID': CLIENT_ID, 'Authorization': f'Bearer {BEARER}'}, "data" : ""}
NUMBER_OF_GAMES = 500 #Total number of games to load into database
RESULTS_PER_QUERY = 500  #Max results per query is 500

### User Parameters ###
NUMBER_OF_USERS = 100
descriptors = ["Little", "Big", "Small", "Hidden", "Crazy", "Blue", "Red", "Green", "Yellow", "Rainbow", "Silly"]
usernames = ["Mario", "Link", "Zelda", "Luigi", "Yoshi", "DonkeyKong", "Sonic", "Peach", "Steve", "Mastercheif", "Pikachu", "Goomba", "Bowser"]

### Review Parameters ###
AVG_REVIEWS_PER_GAME = 10
reviews = ["Great game!", "I hated this.", ":(", "This is maybe the best thing I've ever played in my life!", "This was so horrible", "Ok!", 
           "It was alright", "I've played better.", "I can't believe this cost money.", "How to refund?", 
           "I would sacrifice my first born to play this for the first time again"]
start_date = datetime(2020, 1, 1)
end_date = datetime.now()

### List Parameters ###
USER_WITH_LIST_PERCENT = 0.5
list_names = ["Worst games of all time", "{username}'s list of best games of all time", "Recommend", "Temp", "My list", "Good", "2024 Ranked", 
              "Games to play on the train", "Games to play on the plane", "Games to never play on the train", "Made me cry", "Good stories",
              "Wishlist", "Play later", "These look good", "Interesting", "Try out?"]

###########################################################- Population and Deletion Methods -###########################################################

def populate_games():
    print("Populating games...")
    query_count = 0
    for games_left in range(NUMBER_OF_GAMES, 0, -RESULTS_PER_QUERY):

        offset = query_count * RESULTS_PER_QUERY
        games_this_query = min(RESULTS_PER_QUERY, games_left)

        request = BASE_REQUEST
        request['data'] += "fields name, summary, genres.name, cover.image_id, slug;"                     #Fields we want
        request['data'] += f"limit {games_this_query};"                                                   #Maximum results per query, API only allows up to 500
        request['data'] += f"offset {offset};"                                                            #Offsets the results
        request['data'] += "where version_parent =n & cover!=n & rating_count >= 0 & parent_game =n;"     #Found this mixture of parameters removes most of the console editions and dlcs of games etc.
        request['data'] += "sort rating_count desc;"                                                      #Only get the "good/popular" games first, still gets alot of weird ones first

        response = requests.post('https://api.igdb.com/v4/games', **BASE_REQUEST)
        games_data = response.json()

        for entry in games_data:
            try:
                name = entry['name'] 
                slug = entry['slug']
                if 'summary' in entry:
                    description = entry['summary']
                if 'genres' in entry:
                    genre = entry['genres'][0]['name']
                if 'cover' in entry:
                    picture = entry['cover']['image_id']

                game = Game(id = slug, title = name, description = description, genre = genre, pictureId = picture)
                game.save()
            except Exception as e:
                print(e)
                continue
            
        query_count+=1
        print(f"{Game.objects.count()}/{NUMBER_OF_GAMES}")
    print("Games populated!")

def populate_users():
    print("Populating authors and users...")
    for i in range(NUMBER_OF_USERS):
        try:
            username = random.choice(descriptors) +  random.choice(usernames) + str(random.randint(1000, 9999))
            password = username #use username for password so it is easy to sign in to test account
            email = username +"@email.com" #fake email
            user = User.objects.create_user(username, email, password)

            author = Author(user = user)
            author.save()
        except Exception as e:
            print(e)
            continue
    print(f"User and Author populated with {Author.objects.count()} entries!")

def populate_reviews():
    print("Populating reviews...")
    number_of_users = User.objects.count()
    for game in Game.objects.all():

        avg_rating = random.randint(1, 10)
        number_of_reviews =int(abs(random.normal(loc = 1, scale = 1))*AVG_REVIEWS_PER_GAME)     #Random number of reviews for each game
        number_of_reviews = min(number_of_reviews, number_of_users)                             #Dont want more reviews than users
        number_of_reviews = max(0, number_of_reviews)                                           #Dont want negative number of reviews
        authors = Author.objects.order_by('?')[:number_of_reviews]                              #Gets a random user for each review

        game.views = number_of_reviews * NUMBER_OF_USERS
        game.save()
        
        for author in authors:             
            try:                    
                content = random.choice(reviews)                                          #Generate random content for review
                rating = int(random.normal(loc = avg_rating, scale = 2))                  #Generates reviews normally around a point for more realism
                views = random.randint(0, game.views)                                     #A review shoudln't have more views than the game
                likes = int(views * random.random()*0.5)                                  #Likes will be a percentage of the views
                random_date = end_date - timedelta(random.randint(1,1000))                #Generate random date
                datePosted = random_date
                
                review = Review(author = author, game = game, rating = rating, content = content, likes = likes, views = views, datePosted = datePosted)
                review.save()
            except Exception as e:
                print(e)
                continue
    print(f"Reviews populated with {Review.objects.count()} entries!")

def populate_lists():
    print("Populating lists and List Entries...")
    for author in Author.objects.all():
        #Not every user is gonna have lists
        if(random.random() > USER_WITH_LIST_PERCENT):
            continue
        
        for i in range(1, 5):
            try:
                #Make List
                list_name = random.choice(list_names).format(username = author.user.username)
                description = random.choice(["", "This is just a placeholder list description rather than nothing."])
                list = List(author = author, title = list_name, description = description)
                list.save()
                
                #Add entries
                number_of_games = random.randint(5, 30)
                games = Game.objects.order_by('?')[:number_of_games]    #Get first x random games

                for game in games:
                    listEntry = ListEntry(list = list, game = game)
                    listEntry.save()
            except Exception as e:
                print(e)
                continue

    print(f"List populated with {List.objects.count()} entries!")
    print(f"List Entries populated with {ListEntry.objects.count()} entries!")

def clear_database():
    print("Deleting all records...")
    print("This may take a while")
    ENTRIES_DELETED = 500
    try:
        count = 0

        count += ListEntry.objects.count()
        for i in range(0, ListEntry.objects.count(), ENTRIES_DELETED):
            pks = (ListEntry.objects.all().values_list('pk')[:ENTRIES_DELETED])
            ListEntry.objects.filter(pk__in=pks).delete()

        count += List.objects.count()
        for i in range(0, List.objects.count(), ENTRIES_DELETED):
            pks = (List.objects.all().values_list('pk')[:ENTRIES_DELETED])
            List.objects.filter(pk__in=pks).delete()

        count += Review.objects.count()
        for i in range(0, Review.objects.count(), ENTRIES_DELETED):
            pks = (Review.objects.all().values_list('pk')[:ENTRIES_DELETED])
            Review.objects.filter(pk__in=pks).delete()

        count += Game.objects.count()
        for i in range(0, Game.objects.count(), ENTRIES_DELETED):
            pks = (Game.objects.all().values_list('pk')[:ENTRIES_DELETED])
            Game.objects.filter(pk__in=pks).delete()

        count += Author.objects.count()
        for i in range(0, Author.objects.count(), ENTRIES_DELETED):
            pks = (Author.objects.all().values_list('pk')[:ENTRIES_DELETED])
            Author.objects.filter(pk__in=pks).delete()

        users = User.objects.filter(is_superuser = False, is_staff = False)
        count += users.count()
        for i in range(0, users.count(), ENTRIES_DELETED):
            pks = (User.objects.filter(is_superuser = False, is_staff = False).all().values_list('pk')[:ENTRIES_DELETED])
            User.objects.filter(pk__in=pks).delete()
            
        print(f"Successfully deleted {count} records")
    except Exception as e:
        print("Failed to delete records in database!")
        print(e)
        exit()

###########################################################- User Input Methods -###########################################################

def populate():
    use_default_params = confirm("Do you want to use the default population parameters")
    all = True
    if not use_default_params:
        global NUMBER_OF_GAMES
        global NUMBER_OF_USERS
        global AVG_REVIEWS_PER_GAME
        global USER_WITH_LIST_PERCENT
        global SEED

        all = confirm("Do you want populate all databases (User, Review, Author, List and ListEntry), not just the Game database")
        print(f"How many games do you wish to add to the database? Default: {NUMBER_OF_GAMES}")
        NUMBER_OF_GAMES = get_integer_input()
        if all:
            print(f"How many users do you wish to add to the database? Default: {NUMBER_OF_USERS}")
            NUMBER_OF_USERS = get_integer_input()
            print(f"How many reviews should there be on average per game? Default: {AVG_REVIEWS_PER_GAME}")
            AVG_REVIEWS_PER_GAME = get_integer_input()
            print(f"What percentage of users should have a list? Default: {USER_WITH_LIST_PERCENT*100}%")
            USER_WITH_LIST_PERCENT = get_integer_input()/100
            print(f"What seed would you like to use? Default: {SEED}")
            SEED = get_integer_input()
    if confirm("Are you sure you want to populate the database?"):
        random.seed(SEED)
        print("Populating the database...")
        populate_games()
        if all:
            populate_users()
            populate_reviews()
            populate_lists()
    else:
        print("Exiting the population program!")

def get_integer_input():
    answer = input(">>")
    try:
        answer = int(answer)
        return answer
    except:
        print("Please enter a valid integer")
        return get_integer_input()

def confirm(task_to_confirm):
    answer = input(f"{task_to_confirm}? (Y/N)")
    answer = answer.lower()

    if(answer == "y"):
        return True
    elif(answer == "n"):
        return False
    else:
        print("Please enter either Y or N")
        return confirm(task_to_confirm)

def is_database_full():
    if(ListEntry.objects.count() > 0):
        return True
    if(List.objects.count() > 0):
        return True
    if(Review.objects.count() > 0):
        return True
    if(Author.objects.count() > 0):
        return True
    if(Game.objects.count() > 0):
        return True
    if(User.objects.filter(is_superuser = False, is_staff = False).count() > 0):
        return True
    return False

def populate_or_delete():

    answer = input("Do you want to delete the current database or populate it? (D/P)")
    answer = answer.lower()

    if(answer == "p"):
        if(is_database_full()):
            print("Old entries were found in the database. Populating the database with entries could lead to duplicates and errors.")
            if(confirm("Do you want to delete all the old entries before continuing")):
                clear_database()
            else:
                print("Continuing without deleting old entries.")
        populate()
    elif(answer == "d"):
        if(confirm("Are you sure you want to delete all records in database except superusers and staff users")):
            clear_database()
        else:
            exit()
    else:
        print("Please enter either D or P")
        populate_or_delete()

if __name__ == '__main__':
    populate_or_delete()