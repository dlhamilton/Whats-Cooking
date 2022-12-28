# from itertools import chain
from django.shortcuts import render, get_object_or_404
from django.views import generic, View
from .models import Recipes


class RecipesList(generic.ListView):
    model = Recipes
    recipes_list = Recipes.objects.filter(status=1).order_by('-upload_date')
    template_name = 'recipes.html'
    paginate_by = 6
    # result_list = list(chain(recipes_list))


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
            },
        )