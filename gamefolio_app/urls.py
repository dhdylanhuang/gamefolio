from django.urls import path
from gamefolio_app import views

app_name = 'gamefolio_app'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    
    path('accounts/register/', views.MyRegistrationView.as_view(), name='registration_register'),
    path('register_profile/', views.RegisterProfileView.as_view(), name='register_profile'),  
    
    path('profile/<username>/', views.ProfileView.as_view(), name='profile'),
    path('profiles/', views.ListProfilesView.as_view(), name='list_profiles'),
    
    path('lists/', views.ListsView.as_view(), name='lists'),
    path('create_list/', views.CreateListView.as_view(), name='create_list'),
    path('get-game/', views.AddListGame.as_view(), name='get_game'),
    path('<str:author_username>/<slug:slug>/delete/', views.ListDeleteView.as_view(), name='list_delete'),
    path('list/<author_username>/<slug:slug>', views.ListView.as_view(), name='list'),
    path('list/<author_username>/<slug:slug>/edit/', views.EditListView.as_view(), name='list_edit'),
    
    path('suggest/', views.InlineSuggestionsView.as_view(), name='suggest'),
    path('search/', views.SearchView.as_view(), name='search'),
    
    path('game/<slug:game_id>/', views.GamePageView.as_view(), name="game"),
    path('like_review/', views.LikeReviewView.as_view(), name='like_review'),

    path('add_to_list_form/<slug:slug>/<slug:game_id>/', views.AddToListFormView.as_view(), name='add_to_list_form'),
]

