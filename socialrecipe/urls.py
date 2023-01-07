from . import views
from django.urls import path


urlpatterns = [
    path('', views.HomeList.as_view(), name='home'),
    path('recipes/', views.RecipesList.as_view(), name='recipes'),
    path('recipes/search/', views.RecipesList.as_view(), name='recipes_search'),
    path('recipes/<slug:slug>/', views.RecipeDetail.as_view(), name='recipe_detail'),
    path('favourite/<slug:slug>', views.RecipeFavourite.as_view(), name='recipe_favourite'),
    path('users/<slug:username>/', views.ProfilePage.as_view(), name='profile_page'),
    path('loggedIn/', views.CurrentUserProfileRedirectView.as_view(), name='logged_on'),
    path('users/<slug:username>/myshopping/', views.ProfileShoppingList.as_view(), name='profile_page_shopping'),
    path('users/<slug:username>/myshopping/<slug:list>', views.ProfileSingleList.as_view(), name='profile_single_shopping'),
    path('users/<slug:username>/myrecipes/', views.Profilerecipes.as_view(), name='profile_page_recipes'),
    path('users/<slug:username>/myfollowers/', views.ProfileFollowers.as_view(), name='profile_page_followers'),
    path('users/<slug:username>/myfavourites/', views.ProfileFavourites.as_view(), name='profile_page_favourites'),
]
