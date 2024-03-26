from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, render, render_to_response
from django.http import HttpResponse
from django.views import View
from gamefolio_app.forms import AuthorForm, ReviewForm, UserForm
from django.contrib.auth import authenticate, login
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from gamefolio_app.models import Author, List, ListEntry
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from gamefolio_app.models import Game, Review
from django.db.models import Sum
from registration.backends.simple.views import RegistrationView

class IndexView(View):
    def get(self, request):
        game_list = sorted(Game.objects.all(), key = lambda p : p.average_rating())[:5]
        reviews_list = Review.objects.order_by('-likes')[:6]
        
        context_dict = {}
        context_dict['games'] = game_list
        context_dict['reviews'] = reviews_list
        
        return render(request, 'gamefolio_app/index.html', context=context_dict)
      
class MyRegistrationView(RegistrationView):
    def get_success_url(self, user=None):
        return reverse('gamefolio_app:register_profile')
    

@method_decorator(login_required, name='dispatch')
class RegisterProfileView(View):

    def get(self, request):
        form = AuthorForm()
        context = {'form': form}
        return render(request, 'gamefolio_app/profile_registration.html', context)

    def post(self, request):
        form = AuthorForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()
            return redirect(reverse('gamefolio_app:index'))
        else:
            print(form.errors)

        context = {'form': form}
        return render(request, 'gamefolio_app/profile_registration.html', context)
    

class UserLoginView(View):
    template_name = 'gamefolio_app/registration/login.html'  

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('gamefolio_app:profile'))
            else:
                return HttpResponse("Your Gamefolio account is disabled")
        else:
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")


@method_decorator(login_required, name='dispatch')
class UserLogoutView(LogoutView):
    next_page = reverse_lazy('gamefolio_app:index')
    
class ProfileView(View):
    def get_user_details(self, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        user_profile = Author.objects.get_or_create(user=user)[0]
        form = AuthorForm({'website': user_profile.website, 'picture': user_profile.picture})

        return (user, user_profile, form)
    

    @method_decorator(login_required)
    
    def get(self, request, username):
        try:
            (user, user_profile, form) = self.get_user_details(username)
            user_reviews = Review.objects.filter(author=user_profile)
        except TypeError:
            return redirect(reverse('gamefolio_app:index'))

        sort_reviews_by = request.GET.get('sort_reviews', 'recent')

        if sort_reviews_by == 'liked':
            user_reviews = user_reviews.annotate(likes_total=Sum('likes')).order_by('-likes_total', '-datePosted')
        else:
            user_reviews = user_reviews.order_by('-datePosted')

        context_dict = {'user_profile': user_profile, 'selected_user': user, 'form': form, 'user_reviews': user_reviews}
        return render(request, 'gamefolio_app/profile.html', context_dict)
    
    @method_decorator(login_required)
    def post(self, request, username):
        try:
            (user, user_profile, form) = self.get_user_details(username)
        except TypeError:
            return redirect(reverse('gamefolio_app:index'))
        
        if request.user != user:
            return HttpResponse("Unauthorized access")
            
        form = AuthorForm(request.POST, request.FILES, instance=user_profile)

        if form.is_valid():
            form.save(commit=True)
            return redirect('gamefolio_app:profile', user.username)
        else:
            print(form.errors)

        context_dict = {'user_profile': user_profile, 'selected_user': user, 'form': form}
        return render(request, 'gamefolio_app/profile.html', context_dict)


class ListProfilesView(View):
    @method_decorator(login_required)
    def get(self, request):
        sort_by = request.GET.get('sort_by', 'reviews')
        profiles = Author.objects.annotate(total_reviews=Count('review'), total_likes=Sum('review__likes'))
        
        if sort_by == 'likes':
            profiles = profiles.order_by('-total_likes')
        else:
            profiles = profiles.order_by('-total_reviews')
            
        return render(request,'gamefolio_app/list_profiles.html',{'authors': profiles})
    
class GamePageView(View):
    def get(self, request, game_id):
        game = get_object_or_404(Game, id=game_id)
        if request.user.is_authenticated:
            reviews = Review.objects.filter(game=game).exclude(author__user=request.user)
            user_reviews = Review.objects.filter(game=game).filter(author__user=request.user)
        else:
            reviews = Review.objects.filter(game=game)
            user_reviews = Review.objects.none()
        related_games = Game.objects.filter(genre=game.genre).exclude(id=game_id).order_by('?')[:4]

        if(len(related_games) < 4):
            related_games = Game.objects.all().exclude(id=game_id).order_by('?')[:4]
  
        sort_reviews_by = request.GET.get('sort_reviews', 'recent')
        
        if sort_reviews_by == 'liked':
            reviews = reviews.annotate(likes_total=Sum('likes')).order_by('-likes_total', '-datePosted')
        elif sort_reviews_by == 'recent':
            reviews = reviews.order_by('-datePosted')
        elif sort_reviews_by == 'rating':
            reviews = reviews.order_by('-rating')
        
        form = ReviewForm()

        lists_to_add=[]
        if(request.user.is_authenticated):   
            game = Game.objects.get(id=game_id)
            lists = List.objects.filter(author__user=request.user)
            entries = ListEntry.objects.filter(list__in = lists, game = game).values("list_id")
            lists_to_add = lists.exclude(pk__in=entries)

        context = {
            'game': game,
            'reviews': reviews,
            "user_reviews": user_reviews,
            'form': form,  
            "review_ratings": get_game_ratings(game_id),
            'related_games': related_games,
            "stype": sort_reviews_by,
            "lists_to_add": lists_to_add,
        }
        return render(request, 'gamefolio_app/game.html', context)

    def post(self, request, game_id):
        game = get_object_or_404(Game, id=game_id)
        reviews = Review.objects.filter(game=game_id)

        form = ReviewForm(request.POST)  

        if form.is_valid():
            review = form.save(commit=False)
            review.game = game  
            review.author = request.user.author  
            review.save()
            return redirect('gamefolio_app:game', game_id=game_id)
        
        context = {
            'game': game,
            'reviews': reviews,
            'form': form,
            "review_ratings": get_game_ratings(game_id),
        }
        return render(request, 'gamefolio_app/game.html', context)
    
class SearchView(View):
    def get(self, request):
        
        #Parameters
        MAX_RESULTS_PER_PAGE = 8
        SQL_QUERY = f"""
        SELECT G.id, title, pictureID, genre, avg(rating) AS average
        FROM gamefolio_app_game G LEFT JOIN gamefolio_app_review R
            ON G.id == R.game
        """
        #We do a LEFT JOIN to include games with 0 reviews
        
        #Getting URL parameters
        params = []
        try:
            query = request.GET['query'].strip()
            if(query != ""):
                SQL_QUERY += f"WHERE title LIKE %s\n"
                params.append("%"+query+"%")
        except Exception as e:
            query = ""
        
        try:
            page = request.GET['page'].strip()
        except Exception as e:
            page = 0

        try:
            genre = request.GET['genre'].strip()
            joining_word = "AND" if "LIKE" in SQL_QUERY else "WHERE"
            SQL_QUERY += f"{joining_word} genre = %s\n"
            params.append(genre)
        except Exception as e:
            genre = ""

        try:
            sort = request.GET['sort'].strip()
        except:
            sort = 0

        #Prevent duplicate results
        SQL_QUERY += "GROUP BY G.id, title, genre\n"

        #Sorting
        if sort == "rd":                   #Rating Descending
            SQL_QUERY += "ORDER BY average DESC"
        elif sort == "ra":                 #Rating Ascending
            SQL_QUERY += "ORDER BY average ASC"
        elif sort ==  "vd":                #Views Descending
            SQL_QUERY += "ORDER BY G.views DESC"
        elif sort ==  "va":                #Views Ascending
            SQL_QUERY += "ORDER BY G.views ASC"
        elif sort ==  "ta":                #Title Ascending
            SQL_QUERY += "ORDER BY title ASC"
        elif sort ==  "td":                #Title Descending
            SQL_QUERY += "ORDER BY title DESC"

        results = Game.objects.raw( SQL_QUERY, params )
        result_count = len(results)
        page_count = result_count/MAX_RESULTS_PER_PAGE
        if(page_count == int(page_count)):
            page_count = int(page_count)
        else:
            page_count = int(page_count) + 1
        page_count = max(page_count,1)
        
        try:
            page = int(page)
            assert(page >= 0)
            assert(page < page_count)
        except Exception as e:
            print(e)
            raise Http404 

        offset = page * MAX_RESULTS_PER_PAGE
        actual_results = results[offset:MAX_RESULTS_PER_PAGE+offset]
        current_page = page + 1

        pages = calculate_pages(page_count, current_page)

        def get_unique_genres():
            return  Game.objects.values('genre').distinct()
        genres = get_unique_genres()

        sort_name = {0: "Relevance", "rd": "Rating ▼", "ra": "Rating ▲", "vd": "Views ▼", "va" : "Views ▲", "ta": "Alphabetical ▼", "td": "Alphabetical ▲"}[sort]

        context_dict = {"results" : actual_results, "query" : query, "count": result_count, "pages": pages, "current_page": current_page, "page_count": page_count, "current_genre": genre, "genres": genres, "sort_id": sort, "sort_name": sort_name}
        return render(request, 'gamefolio_app/search.html', context_dict)
    
#Helper Functions
def handler404(request, exception, template_name="gamefolio_app/404.html"):
    response = render_to_response(template_name)
    response.status_code = 404
    return response

def get_game_ratings(game_id):

    class RatingDistribution():

        def __init__(self, rating, count):
            self.rating = ["½", "★", "★½","★★", "★★½", "★★★", "★★★½", "★★★★", "★★★★½", "★★★★★"][rating-1]
            self.count = count
            self.height = 0

        def set_height(self, max_count):
            if(max_count == 0):
                self.height = 10
                return
            self.height = (self.count/max_count) * 90 + 10
            
    reviews = []
    max_count = 0
    for i in range(10):
        count = Review.objects.filter(game=game_id, rating=i+1).aggregate(Count("rating"))["rating__count"]
        rating = RatingDistribution(i+1, count)
        max_count = max(count, max_count)
        reviews.append(rating)

    for rating in reviews:
        rating.set_height(max_count)

    return reviews