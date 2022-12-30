# from itertools import chain
from django.shortcuts import render, get_object_or_404, reverse
from django.views import generic, View
from django.http import HttpResponseRedirect
from .models import Recipes
from .forms import CommentsForm
from django.db.models import Count


class HomeList(View):
    def get(self, request, *args, **kwargs):
        top_recipes = Recipes.objects.filter(status=1).order_by('favourites')
        top_users = top_recipes.annotate(count=Count('author_id')).order_by('count')

        return render(
            request,
            "index.html",
            {
                # "top_recipes": top_recipes,
                "top_users": top_users,
                "page_name": "Home",
            }
        )


# class RecipesList(generic.ListView):
#     model = Recipes
#     recipes_list = Recipes.objects.filter(status=1).order_by('-upload_date')
#     template_name = 'recipes.html'
#     paginate_by = 6
#     # result_list = list(chain(recipes_list))


class RecipesList(View):
    def get(self, request, *args, **kwargs):
        recipes_list = Recipes.objects.filter(status=1).order_by('-upload_date')

        return render(
            request,
            "recipes.html",
            {
                "recipes_list": recipes_list,
                "paginate_by": 6,
                "page_name": "Recipes",
            }
        )


class RecipeDetail(View):
    def get(self, request, slug, *args, **kwargs):
        queryset = Recipes.objects.filter(status=1)
        recipe = get_object_or_404(queryset, slug=slug)
        recipe_methods = recipe.methods.order_by('order')
        recipe_comments = recipe.comments.filter(status=1).order_by('-post_date')
        recipe_ingredients = recipe.recipe_items.filter()
        recipe_images = recipe.recipe_images.filter()
        favourited = False
        if recipe.favourites.filter(id=self.request.user.id).exists():
            favourited = True

        return render(
            request,
            "recipe_detail.html",
            {
                "recipe": recipe,
                "methods": recipe_methods,
                "favourited": favourited,
                "comments": recipe_comments,
                "ingredients": recipe_ingredients,
                "images": recipe_images,
                "page_name": recipe.title,
                "commented": False,
                "valid_comment": True,
                "comment_form": CommentsForm(),
            },
        )

    def post(self, request, slug, *args, **kwargs):
        queryset = Recipes.objects.filter(status=1)
        recipe = get_object_or_404(queryset, slug=slug)
        recipe_methods = recipe.methods.order_by('order')
        recipe_comments = recipe.comments.filter(status=1).order_by('-post_date')
        recipe_ingredients = recipe.recipe_items.filter()
        recipe_images = recipe.recipe_images.filter()
        favourited = False
        if recipe.favourites.filter(id=self.request.user.id).exists():
            favourited = True

        comment_form = CommentsForm(data=request.POST)

        if comment_form.is_valid():
            comment_form.instance.user = request.user
            comment = comment_form.save(commit=False)
            comment.recipe = recipe
            comment.save()
            valid_comment = True
        else:
            comment_form = CommentsForm()
            valid_comment = False

        return render(
            request,
            "recipe_detail.html",
            {
                "recipe": recipe,
                "methods": recipe_methods,
                "favourited": favourited,
                "comments": recipe_comments,
                "ingredients": recipe_ingredients,
                "images": recipe_images,
                "page_name": recipe.title,
                "commented": True,
                "valid_comment": valid_comment,
                "comment_form": CommentsForm(),
            },
        )


class RecipeFavourite(View):
    def post(self, request, slug):
        recipe = get_object_or_404(Recipes,slug=slug)

        if recipe.favourites.filter(id=request.user.id).exists():
            recipe.favourites.remove(request.user)
        else:
            recipe.favourites.add(request.user)
        return HttpResponseRedirect(reverse('recipe_detail', args=[slug]))