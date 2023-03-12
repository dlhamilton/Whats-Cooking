"""
Admin.py
"""
from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
import socialrecipe.models


@admin.register(socialrecipe.models.UserDetails)
class UserDetailsAdmin(admin.ModelAdmin):
    """
    User Details Admin
    """
    list_display = (
        'user',
        'status',
        'location')
    search_fields = [
        'user__username',
        'user__first_name',
        'user__last_name',
        'user__email']


@admin.register(socialrecipe.models.RecipeImages)
class RecipeImagesAdmin(admin.ModelAdmin):
    """
    Recipe Images Admin
    """
    list_display = (
        'recipe',
        'user',
        'upload_date')
    search_fields = [
        'recipe__title',
        'user',
        'user__first_name',
        'user__last_name',
        'user__email',
        'user__username']
    list_filter = (
        'user__username',
        'upload_date')


@admin.register(socialrecipe.models.Comments)
class CommentsAdmin(admin.ModelAdmin):
    """
    Comments Admin
    """
    list_display = (
        'user',
        'recipe',
        'status',
        'post_date')
    search_fields = [
        'user__first_name',
        'user__last_name',
        'user__email',
        'body',
        'recipe_title']
    list_filter = ('post_date', 'status')
    actions = ['remove_comment']

    def remove_comment(self, request, queryset):
        '''
        remove a bad comment
        '''
        queryset.update(status=3)


@admin.register(socialrecipe.models.Recipes)
class RecipeAdmin(admin.ModelAdmin):
    """
    Recipe Admin
    """
    list_display = (
        'title',
        'slug',
        'status',
        'author',
        'upload_date')
    search_fields = [
        'title',
        'author__email',
        'author__username',
        'author__first_name',
        'author__last_name']
    prepopulated_fields = {'slug': ('author', 'title')}
    list_filter = ('status', 'upload_date')
    summernote_fields = ('excerpt')


@admin.register(socialrecipe.models.Methods)
class MethodsAdmin(SummernoteModelAdmin):
    """
    Methods of recipes Admin
    """
    list_display = ('recipe', 'order')
    list_filter = ('recipe', 'order')
    search_fields = ('recipe', 'order', 'method')
    summernote_fields = ('method')


@admin.register(socialrecipe.models.Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    """
    Ingredients Admin
    """
    list_display = ('name', 'approved')
    search_fields = ['name']
    actions = ['approve_ingredients']

    def approve_ingredients(self, request, queryset):
        '''
        approve that an ingrident is valid
        '''
        queryset.update(approved=True)


@admin.register(socialrecipe.models.StarRating)
class StarRatingAdmin(admin.ModelAdmin):
    """
    Star rating of recipe Admin
    """
    list_display = (
        'recipe',
        'user',
        'rating',
        'date_given')
    search_fields = [
        'recipe__title',
        'user__first_name',
        'user__last_name',
        'user__email',
        'user__username']
    list_filter = ('recipe__title', 'user__username', 'rating')


@admin.register(socialrecipe.models.RecipeItems)
class RecipeItemsAdmin(admin.ModelAdmin):
    """
    Recipe Items Admin
    """
    list_display = ('recipe', 'ingredients', 'amount', 'unit')
    search_fields = ['recipe__title', 'ingredients__name']


@admin.register(socialrecipe.models.Units)
class UnitsAdmin(admin.ModelAdmin):
    """
    Units Admin
    """
    search_fields = ['name']
    list_display = ['name']
