from django.contrib import admin
import socialrecipe.models
from django_summernote.admin import SummernoteModelAdmin


@admin.register(socialrecipe.models.UserDetails)
class UserDetailsAdmin(admin.ModelAdmin):
    list_display = ('user','status', 'location')
    search_fields = ['user__username', 'user__first_name', 'user__last_name','user__email']


@admin.register(socialrecipe.models.RecipeImages)
class RecipeImagesAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user', 'upload_date')
    search_fields = ['recipe__title', 'user', 'user__first_name', 'user__last_name','user__email', 'user__username']
    list_filter = ('user__username', 'upload_date')


@admin.register(socialrecipe.models.Comments)
class CommentsAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'status', 'post_date')
    search_fields = ['user__first_name', 'user__last_name','user__email', 'body', 'recipe_title']
    list_filter = ('post_date', 'status')
    def remove_comment(self, request, queryset):
        queryset.update(status=3)


@admin.register(socialrecipe.models.Recipes)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'status', 'author', 'upload_date')
    search_fields = ['title', 'author__email', 'author__username', 'author__first_name', 'author__last_name']
    prepopulated_fields = {'slug': ('author', 'title')}
    list_filter = ('status', 'upload_date')
    summernote_fields = ('excerpt')


@admin.register(socialrecipe.models.Methods)
class MethodsAdmin(SummernoteModelAdmin):
    list_display = ('recipe', 'order')
    list_filter = ('recipe', 'order')
    search_fields = ('recipe', 'order', 'method')
    summernote_fields = ('method')

@admin.register(socialrecipe.models.Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'approved')
    search_fields = ['name']

    def approve_ingredients(self, request, queryset):
        queryset.update(approved=True)


@admin.register(socialrecipe.models.ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'date_made')
    search_fields = ['name', 'user__first_name', 'user__last_name', 'user__email']
    list_filter = ('user__username', 'date_made')


@admin.register(socialrecipe.models.ShoppingListItems)
class ShoppingListItemsAdmin(admin.ModelAdmin):
    list_display = ('list', 'ingredients', 'amount', 'unit')
    search_fields = ['list__name', 'ingredients']


@admin.register(socialrecipe.models.StarRating)
class StarRatingAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user', 'rating', 'date_given')
    search_fields = ['recipe__title', 'user__first_name', 'user__last_name', 'user__email', 'user__username']
    list_filter = ('recipe__title', 'user__username', 'rating')


@admin.register(socialrecipe.models.RecipeItems)
class RecipeItemsAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredients', 'amount', 'unit')
    search_fields = ['recipe__title', 'ingredients__name']


@admin.register(socialrecipe.models.Units)
class UnitsAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name']