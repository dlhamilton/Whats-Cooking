# from itertools import chain
from django.shortcuts import render, get_object_or_404, reverse,redirect
from django.views import generic, View
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import RedirectView
from .models import Recipes, User, UserDetails, ShoppingList,StarRating
from .forms import CommentsForm
from django.db.models import Count, Avg


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
        recipes_avg = StarRating.objects.filter(recipe=recipe).aggregate(Avg('rating')).get('rating__avg')
        recipes_count = StarRating.objects.filter(recipe=recipe).count()
        star_loop = range(0, int(recipes_avg))
        empty_star_loop = range(0, 5-int(recipes_avg))
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
                "recipes_avg": recipes_avg,
                "recipes_count": recipes_count,
                "star_loop": star_loop,
                "empty_star_loop": empty_star_loop,
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
            return JsonResponse({'liked': False})
        else:
            recipe.favourites.add(request.user)
        # return HttpResponseRedirect(reverse('recipe_detail', args=[slug]))
        return JsonResponse({'liked': True})


class ProfilePage(View):
    def get(self, request, username, *args, **kwargs):

        # top_recipes = UserDetails.objects.filter(status=1)
        page_name = get_object_or_404(User, username=username)

        # page_name = get_object_or_404(queryset, username=username)
        fav_recipes=[]
        all_recipes = Recipes.objects.filter(status=1)
        
        for r in all_recipes:
            if r.favourites.filter(id=page_name.id).exists():
                fav_recipes.append(r)
        is_following_data = 0
        if request.user.is_authenticated:
            is_following = page_name.user_details.get_followers()
            if page_name.user_follows.filter(user=request.user).exists():
                is_following_data = 2
            else:
                is_following_data = 1

    # user is not in the list
        return render(
            request,
            "user_profile_page.html",
            {
                "page_name": page_name,
                "fav_recipes": fav_recipes,
                "fav_recipes_count": len(fav_recipes),
                "logged_in_user": request.user.username,
                "is_following": is_following_data,
            }
        )


class ProfileShoppingList(View):
    def get(self, request, username, *args, **kwargs):

        if username == request.user.username:
            recipes_count = Recipes.objects.filter(author=request.user.id).filter(status=1).count()
            return render(
                request,
                "shopping_lists.html",
                {
                    "page_name": request.user,
                    "logged_in_user": request.user,
                    "fav_recipes_count": recipes_count,
                }
            )
        else:
            return HttpResponseRedirect(reverse('profile_page', kwargs={'username': request.user.username}))


class ProfileSingleList(View):
    def get(self, request, username, list, *args, **kwargs):

        if username == request.user.username:
            shopping_list = get_object_or_404(ShoppingList, slug=list)
            user_list_items = shopping_list.shopping_list_items.filter()
            recipes_count = Recipes.objects.filter(author=request.user.id).filter(status=1).count()
            
            return render(
                request,
                "shopping_list.html",                
                {
                    "page_name": request.user,
                    "logged_in_user": request.user,
                    "user_list": user_list_items,
                    "user_shopping_list": shopping_list,
                    "fav_recipes_count": recipes_count,
                }
            )
        else:
            return HttpResponseRedirect(reverse('profile_page', kwargs={'username': request.user.username}))


class Profilerecipes(View):
    def get(self, request, username, *args, **kwargs):
        page_name = get_object_or_404(User, username=username)
        recipes_count = Recipes.objects.filter(author=page_name.id).filter(status=1).count()
        recipe = Recipes.objects.filter(author=page_name.id).filter(status=1)
        count = 0
        recipes_avg=[]
        
        total_rec = 0
        for i in recipe:
            recipes_avg.append( StarRating.objects.filter(recipe=i).aggregate(Avg('rating')))      
            total_rec = total_rec + recipes_avg[count].get('rating__avg')
            count = count+1
        if count != 0 :
            user_recipe_average = total_rec/count
        else:
            user_recipe_average = 0

        return render(
            request,
            "user_recipes.html",
            {
                "page_name": page_name,
                "logged_in_user": request.user,
                "fav_recipes_count": recipes_count,
                "average_recipe": user_recipe_average,
            }
        )


class ProfileFollowers(View):
    def get(self, request, username, *args, **kwargs):
        page_name = get_object_or_404(User, username=username)
        recipes_count = Recipes.objects.filter(author=page_name.id).filter(status=1).count()

        return render(
            request,
            "user_followers.html",
            {
                "page_name": page_name,
                "logged_in_user": request.user,
                "fav_recipes_count": recipes_count,
            }
        )


class ProfileFavourites(View):
    def get(self, request, username, *args, **kwargs):
        page_name = get_object_or_404(User, username=username)
        all_recipes = Recipes.objects.filter(status=1)
        fav_recipes = []
        for r in all_recipes:
            if r.favourites.filter(id=page_name.id).exists():
                fav_recipes.append(r)
        
        return render(
            request,
            "user_favourites.html",
            {
                "page_name": page_name,
                "logged_in_user": request.user,
                "fav_recipes": fav_recipes,
                "fav_recipes_count": len(fav_recipes),
            }
        )


class CurrentUserProfileRedirectView(LoginRequiredMixin, RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        return reverse('profile_page', kwargs={'username': self.request.user.username})
        #return redirect("profile_page", slug=username)