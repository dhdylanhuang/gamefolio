from django.urls import path
from gamefolio_app import views

app_name = 'gamefolio_app'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    
    path('accounts/register/', views.MyRegistrationView.as_view(), name='registration_register'),
    path('register_profile/', views.RegisterProfileView.as_view(), name='register_profile'),  # Corrected line

    path('profile/<username>/', views.ProfileView.as_view(), name='profile'),
    path('profiles/', views.ListProfilesView.as_view(), name='list_profiles'),
]
