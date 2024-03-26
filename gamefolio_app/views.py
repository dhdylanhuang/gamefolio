from django.db.models import Count, Sum
from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.views import View
from gamefolio_app.forms import AuthorForm, UserForm
from django.contrib.auth import authenticate, login
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from gamefolio_app.models import Author
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
    
#Helper Functions
def handler404(request, exception, template_name="gamefolio_app/404.html"):
    response = render_to_response(template_name)
    response.status_code = 404
    return response