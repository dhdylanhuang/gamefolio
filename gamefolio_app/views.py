from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.db.models import Avg, Count, Sum
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from registration.backends.simple.views import RegistrationView
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from gamefolio_app.forms import ReviewForm, UserForm , AuthorForm, CreateListForm
from gamefolio_app.models import Game, Review, Author, List, ListEntry
from django.core.paginator import Paginator
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render_to_response
from django.http import Http404 

class IndexView(View):
    def get(self, request):
        game_list = Game.objects.annotate(average_ratings=Avg('review__rating')).order_by('-average_ratings')[:4]
        reviews_list = Review.objects.order_by('-likes')[:6]
        visitor_cookie_handler(request)
        
        context_dict = {}
        context_dict['games'] = game_list
        context_dict['reviews'] = reviews_list
        context_dict['visits'] = request.session['visits']
        
        return render(request, 'gamefolio_app/index.html', context=context_dict)
      
class MyRegistrationView(RegistrationView):
    def form_invalid(self, form):
        response = super().form_invalid(form)
        for field, errors in form.errors.items():
            field_name = form.fields[field].label
            for error in errors:
                messages.error(self.request, f"{field_name}: {error}")
        return response

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
    next_page = reverse_lazy('gamefolio_app:auth_logout')
    
class ProfileView(View):
    def get_user_details(self, username):
        try:
            user = User.objects.get(username=username)
            lists = List.objects.filter(author=user.author)
        except User.DoesNotExist:
            return None
        user_profile = Author.objects.get_or_create(user=user)[0]
        form = AuthorForm({'website': user_profile.website, 'picture': user_profile.picture, 'bio': user_profile.bio})

        return (user, lists, user_profile, form)
    
    def get(self, request, username):
        try:
            (user, lists, user_profile, form) = self.get_user_details(username)
            user_reviews = Review.objects.filter(author=user_profile)
            user_reviews = user_reviews.annotate(likes_total=Sum('likes'))
            user_reviews_count = len(user_reviews)
        except TypeError:
            return redirect(reverse('gamefolio_app:index'))
        
        sort_reviews_by = request.GET.get('sort_reviews', 'recent')
        
        if sort_reviews_by == 'liked':
            user_reviews = user_reviews.annotate(likes_total=Sum('likes')).order_by('-likes_total', '-datePosted')
        elif sort_reviews_by == 'recent':
            user_reviews = user_reviews.order_by('-datePosted')
        elif sort_reviews_by == 'rating':
            user_reviews = user_reviews.order_by('-rating')

        context_dict = {'user_profile': user_profile, 'count':user_reviews_count, 'selected_user': user, 'user_lists':lists,'form': form, 'user_reviews': user_reviews, 'sort_reviews_by': sort_reviews_by}
        return render(request, 'gamefolio_app/profile.html', context_dict)
    
    @method_decorator(login_required)
    def post(self, request, username):
        try:
            (user, lists, user_profile, form) = self.get_user_details(username)
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
    def get(self, request):
        MAX_RESULTS_PER_PAGE = 12
        profiles = Author.objects.annotate(total_reviews=Count('review'), total_likes=Sum('review__likes'))
        profiles_count = len(profiles)
        sort_by = request.GET.get('sort', default='likes')
        
        if sort_by == 'reviews':
            profiles = profiles.order_by('-total_reviews')
        elif sort_by == "likes":
            profiles = profiles.order_by('-total_likes')
        elif sort_by == "alphabetical":
            profiles = profiles.order_by('user__username')
                     
        try:
            page = request.GET['page'].strip()
        except Exception as e:
            page = 0
            
        page_count = profiles_count/MAX_RESULTS_PER_PAGE
        
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
        actual_results = profiles[offset:MAX_RESULTS_PER_PAGE+offset]
        current_page = page + 1
        
        pages = calculate_pages(page_count, current_page)
        
        context_dict = {"authors" : actual_results, "count": profiles_count, "pages": pages, "current_page": current_page, "page_count": page_count, "sort_by": sort_by}
        return render(request, 'gamefolio_app/list_profiles.html', context_dict)
      
class ListView(View):
    def get(self, request, author_username, slug):
        list_obj = get_object_or_404(List, author__user__username=author_username, slug=slug)
        list_obj.views += 1
        list_obj.save()      
        list_entries = list_obj.listentry_set.all()
        all_games = Game.objects.all().order_by('title')
        context = {'list_obj': list_obj, 'list_entries': list_entries, 'all_games': all_games, 'views': request.session['visits']}
        return render(request, 'gamefolio_app/list.html', context)
    
    @method_decorator(login_required)
    def post(self, request, author_username, slug):
        list_obj = get_object_or_404(List, author__user__username=author_username, slug=slug)
        if request.user == list_obj.author.user:
            game_id = request.POST.get('game')
            game = get_object_or_404(Game, id=game_id)
            ListEntry.objects.create(list=list_obj, game=game)
        return redirect('gamefolio_app:list', author_username=author_username, slug=slug)

class EditListView(View):
    @method_decorator(login_required)
    def get(self, request, author_username, slug):
        list_obj = get_object_or_404(List, author__user__username=author_username, slug=slug)
        create_list_form = CreateListForm({"title": list_obj.title, "description": list_obj.description})
        list = ListEntry.objects.all()
        context_dict = {
                        'user_list' : list,
                        'form': create_list_form,
                        "title": list_obj.title,
                        "entries": ListEntry.objects.filter(list = list_obj)}
        
        return render(request, 'gamefolio_app/create_list.html', context_dict)
    
    @method_decorator(login_required)
    def post(self, request, author_username, slug): 
        create_list_form = CreateListForm(request.POST)
        create_list_form.is_valid()
        if "title" in create_list_form.data.keys():
            list_obj = get_object_or_404(List, author__user__username=author_username, slug=slug)
            list_obj.description = create_list_form.data["description"]
            list_obj.save()
            listEntries = ListEntry.objects.filter(list = list_obj)
            try:
                games = create_list_form.cleaned_data['games']
            except:
                games = []
            for entry in listEntries:
                if(entry.game not in games):
                    entry.delete()
            for game in games:
                if(len(ListEntry.objects.filter(game=game, list=list_obj))==0):
                    ListEntry.objects.create(list=list_obj, game=game)

            return redirect('gamefolio_app:profile', username=request.user.username)
        else:
            return redirect('gamefolio_app:list_edit', author_username=author_username, slug=slug)

class AddListGame(View):
    @method_decorator(login_required)
    def get(self, request):
        if 'id' in request.GET:
            id = request.GET['id']
        else:
            id = ''
        game = get_object_or_404(Game, id = id) 
        context = {'game': game}
        value = render(request, 'gamefolio_app/list_entry.html', context)
        return value

class CreateListView(View):
    @method_decorator(login_required)
    def get(self, request):
        create_list_form = CreateListForm()
        list = ListEntry.objects.all()
        
        context_dict = {'create_list_form': create_list_form,
                        'user_list' : list,
                        'form': create_list_form,}
        
        return render(request, 'gamefolio_app/create_list.html', context_dict)
    
    @method_decorator(login_required)
    def post(self, request):
        create_list_form = CreateListForm(request.POST)
        create_list_form.is_valid()
        if "title" in create_list_form.data.keys():
            new_list = create_list_form.save(commit=False)
            new_list.author = request.user.author
            new_list.save()
            try:
                games = create_list_form.cleaned_data['games']
            except:
                games = []
            for game in games:
                ListEntry.objects.create(list=new_list, game=game)
            return redirect('gamefolio_app:profile', username=request.user.username)
        else:
            lists = List.objects.all()
            list = ListEntry.objects.all()

            context_dict = {
                'create_list_form': create_list_form,
                'all_lists': lists,
                'user_list': list,
            }

            return render(request, 'gamefolio_app/create_list.html', context_dict)
        
class ListDeleteView(View):
    def post(self, request, author_username, slug):
        list_obj = get_object_or_404(List, author__user__username=author_username, slug=slug)

        if request.user == list_obj.author.user:
            list_obj.delete()
            messages.success(request, "List deleted successfully.")
        else:
            messages.error(request, "You are not authorized to delete this list.")
        
        return redirect(reverse('gamefolio_app:profile', kwargs={'username': author_username}))
    
class ListsView(View):
    def get(self, request):

        MAX_RESULTS_PER_PAGE = 9
        entries = ListEntry.objects.all().values_list("list")
        lists = List.objects.filter(id__in=entries).order_by('-views')
        lists_count = len(lists)
        
        try:
            page = request.GET['page'].strip()
        except Exception as e:
            page = 0

        sort_reviews_by = request.GET.get('sort', 'views')
        
        if sort_reviews_by == 'views':
            lists = lists.order_by('-views', 'title')
        elif sort_reviews_by == 'alphabetical':
            lists = lists.order_by('title')

        page_count = lists_count/MAX_RESULTS_PER_PAGE
        
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
        actual_results = lists[offset:MAX_RESULTS_PER_PAGE+offset]
        current_page = page + 1
        
        pages = calculate_pages(page_count, current_page)
        
        context_dict = {"lists" : actual_results, "count": lists_count, "pages": pages, "current_page": current_page, "page_count": page_count, "sort_reviews_by": sort_reviews_by}
        return render(request, 'gamefolio_app/lists.html', context_dict)
    
class InlineSuggestionsView(View):
    def get(self, request):
        if 'suggestion' in request.GET:
            suggestion = request.GET['suggestion']
        else:
            suggestion = ''
        game_list = get_games_list(max_results=8, starts_with=suggestion)

        if len(game_list) == 0:
            game_list = Game.objects.order_by('title')[:8]
        return_val =  render(request, 'gamefolio_app/games.html', {'games': game_list})
        return return_val
   
class AddToListFormView(View):
    def get(self, request, slug, game_id):
        list = get_object_or_404(List, slug = slug, author = request.user.author)
        game = get_object_or_404(Game, id = game_id)
        ListEntry.objects.create(list = list, game = game)
        return redirect("gamefolio_app:game", game_id = game_id);

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

def handler404(request, exception, template_name="gamefolio_app/404.html"):
    response = render_to_response(template_name)
    response.status_code = 404
    return response

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
    
class LikeReviewView(View):
    @method_decorator(login_required)
    def get(self, request):
        review_id = request.GET.get('review_id')
        try:
            review = Review.objects.get(pk=review_id)
        except Review.DoesNotExist:
            return HttpResponse(-1)
        except ValueError:
            return HttpResponse(-1)
        review.likes += 1
        review.save()
        
        return HttpResponse(review.likes)

    
#Helper Functions
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

def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1')) 
    last_visit_cookie = get_server_side_cookie(request,
                                               'last_visit',
                                               str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],
                                        '%Y-%m-%d %H:%M:%S')

    
    if (datetime.now() - last_visit_time).seconds > 0:
        visits = visits + 1
        request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = last_visit_cookie

    request.session['visits'] = visits

def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

def get_games_list(max_results=0, starts_with=''):
    games_list = []
    if starts_with:
        games_list = Game.objects.filter(title__startswith=starts_with)
    if max_results > 0:
        if len(games_list) > max_results:
            games_list = games_list[:max_results]
    
    return games_list

#Calculates what page buttons we need to show at the bottom
def calculate_pages(page_count, current_page):
    pages = []
    if(page_count <= 5):
        return [i for i in range(1,int(page_count+1))]
    else:
        count = 0
        for i in range(current_page-1, 1, -1):
            if(count == 2):
                break
            count += 1;
            pages.append(i)
        
        count = 0
        for i in range(current_page, page_count, 1):
            if(count == 3):
                break
            count += 1;
            pages.append(i)

        if(1 not in pages):
            pages.append(1)
        if(page_count not in pages):
            pages.append(page_count)

        pages.sort()

        last_page = pages[0]
        jump_index = -1
        i = 0
        for page in pages:
            if(page-last_page > 1):
                jump_index = i
            i+=1
            last_page = page
    
        pages.insert(jump_index, "type")
        return pages

