"""
social recipe urls
"""
from django.urls import path
from . import views


urlpatterns = [
    path(
        '',
        views.HomeList.as_view(),
        name='home'),
    path(
        'recipes/',
        views.RecipesList.as_view(),
        name='recipes'),
    path(
        'recipes/search/',
        views.RecipesList.as_view(),
        name='recipes_search'),
    path(
        'recipes/filter/',
        views.RecipesList.as_view(),
        name='recipes_filter'),
    path(
        'recipes/sort/<sort_type>',
        views.RecipesList.as_view(),
        name='recipes_sort'),
    path(
        'recipes/<slug:slug>/',
        views.RecipeDetail.as_view(),
        name='recipe_detail'),
    path(
        'users/<slug:username>/',
        views.ProfilePage.as_view(),
        name='profile_page'),
    path(
        'loggedIn/',
        views.CurrentUserProfileRedirectView.as_view(),
        name='logged_on'),
    path(
        'users/<slug:username>/myrecipes/',
        views.Profilerecipes.as_view(),
        name='profile_page_recipes'),
    path(
        'users/<slug:username>/myrecipes/new',
        views.ProfileRecipesAdd.as_view(),
        name='profile_page_recipes_add'),
    path(
        'users/<slug:username>/myrecipes/edit/<slug:recipe>',
        views.ProfileRecipesEdit.as_view(),
        name='profile_page_recipes_edit'),
    path(
        'users/<slug:username>/myfollowers/',
        views.ProfileFollowers.as_view(),
        name='profile_page_followers'),
    path(
        'users/<slug:username>/myfavourites/',
        views.ProfileFavourites.as_view(),
        name='profile_page_favourites'),
]
