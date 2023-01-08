# from itertools import chain
from django.shortcuts import render, get_object_or_404, reverse,redirect
from django.views import generic, View
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import RedirectView
from .models import Recipes, User, UserDetails, ShoppingList, StarRating, Ingredients
from .forms import CommentsForm, SearchRecipeForm, FilterRecipeForm
from django.db.models import Count, Avg, Q
from django.urls import resolve


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
def RecipeFilterList(search_list):
    test=[]
    # for i in search_list:
        # test.append(i.name)
    temp_recipes_list = Recipes.objects.filter(status=1)
    for i in search_list:
        temp_recipes_list = temp_recipes_list.filter(Q(recipe_items__ingredients__name__icontains=i.name))
        # test.append(recipes_list)
    
    return temp_recipes_list


class RecipesList(View):
    def get(self, request, *args, **kwargs):
        recipes_list = Recipes.objects.filter(status=1).order_by('-upload_date')
        form = SearchRecipeForm(request.GET)
        filter_form = FilterRecipeForm(request.GET)
        query = True
        if form.is_valid():
            if form.cleaned_data['search_query'] != "": 
                recipes_list = form.cleaned_data['search_query']
                recipes_list = Recipes.objects.filter(status=1).filter(Q(author__username__icontains=recipes_list) | Q(title__icontains=recipes_list)).order_by('-upload_date')

        recipe_elm=[]
        the_path_name = resolve(request.path_info).url_name

        if filter_form.is_valid():
            recipe_elm = filter_form.cleaned_data['filter_query']
            recipes_list = RecipeFilterList(recipe_elm)
            
        if len(recipes_list) == 0:
            recipes_list = "No Recipes Match Your Search"
            query = False

        return render(
            request,
            "recipes.html",
            {
                "recipes_list": recipes_list,
                "paginate_by": 6,
                "page_name": "Recipes",
                'form': form,
                "query": query,
                "filter_form": filter_form,
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
        recipes_avg = StarRating.objects.filter(recipe=recipe).aggregate(Avg('rating')).get('rating__avg')
        recipes_count = StarRating.objects.filter(recipe=recipe).count()
        star_loop = range(0, int(recipes_avg))
        empty_star_loop = range(0, 5-int(recipes_avg))
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
                "recipes_avg": recipes_avg,
                "recipes_count": recipes_count,
                "star_loop": star_loop,
                "empty_star_loop": empty_star_loop,
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


def getAverageRecipeRating(a_user):
    page_name = get_object_or_404(User, username=a_user)
    recipe = Recipes.objects.filter(author=page_name.id).filter(status=1)
    count = 0
    recipes_avg = []
    total_rec = 0
    for i in recipe:
        recipes_avg.append(StarRating.objects.filter(recipe=i).aggregate(Avg('rating')))      
        total_rec = total_rec + recipes_avg[count].get('rating__avg')
        count = count+1
    if count != 0:
        user_recipe_average = total_rec/count
    else:
        user_recipe_average = 0
    thisdict = { 
        "user_recipe_average": user_recipe_average,
        "user_recipe_average_star": range(0, int(user_recipe_average)),
        "user_recipe_average_blank": range(0, 5-int(user_recipe_average)),
    }
    return thisdict


class ProfilePage(View):
    def get(self, request, username, *args, **kwargs):

        # top_recipes = UserDetails.objects.filter(status=1)
        page_name = get_object_or_404(User, username=username)
        user_recipe_average = getAverageRecipeRating(username)
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
                "average_recipe": user_recipe_average,
            }
        )


class ProfileShoppingList(View):
    def get(self, request, username, *args, **kwargs):

        if username == request.user.username:
            recipes_count = Recipes.objects.filter(author=request.user.id).filter(status=1).count()
            user_recipe_average = getAverageRecipeRating(username)
            return render(
                request,
                "shopping_lists.html",
                {
                    "page_name": request.user,
                    "logged_in_user": request.user,
                    "fav_recipes_count": recipes_count,
                    "average_recipe": user_recipe_average,
                }
            )
        else:
            if request.user.is_authenticated:
                return HttpResponseRedirect(reverse('profile_page', kwargs={'username': request.user.username}))
            
            return HttpResponseRedirect(reverse('home'))


class ProfileSingleList(View):
    def get(self, request, username, list, *args, **kwargs):

        if username == request.user.username:
            shopping_list = get_object_or_404(ShoppingList, slug=list)
            user_list_items = shopping_list.shopping_list_items.filter()
            recipes_count = Recipes.objects.filter(author=request.user.id).filter(status=1).count()
            user_recipe_average = getAverageRecipeRating(username)
            return render(
                request,
                "shopping_list.html",                
                {
                    "page_name": request.user,
                    "logged_in_user": request.user,
                    "user_list": user_list_items,
                    "user_shopping_list": shopping_list,
                    "fav_recipes_count": recipes_count,
                    "average_recipe": user_recipe_average,
                }
            )
        else:
            if request.user.is_authenticated:
                return HttpResponseRedirect(reverse('profile_page', kwargs={'username': request.user.username}))
            return HttpResponseRedirect(reverse('home'))

class Profilerecipes(View):
    def get(self, request, username, *args, **kwargs):
        page_name = get_object_or_404(User, username=username)
        recipes_count = Recipes.objects.filter(author=page_name.id).filter(status=1).count()
        recipe = Recipes.objects.filter(author=page_name.id).filter(status=1)
        user_recipe_average = getAverageRecipeRating(username)

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
        user_recipe_average = getAverageRecipeRating(username)
        return render(
            request,
            "user_followers.html",
            {
                "page_name": page_name,
                "logged_in_user": request.user,
                "fav_recipes_count": recipes_count,
                "average_recipe": user_recipe_average,
            }
        )


class ProfileFavourites(View):
    def get(self, request, username, *args, **kwargs):
        user_recipe_average = getAverageRecipeRating(username)
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
                "average_recipe": user_recipe_average,
            }
        )


class CurrentUserProfileRedirectView(LoginRequiredMixin, RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return reverse('profile_page', kwargs={'username': self.request.user.username})
        #return redirect("profile_page", slug=username)  
        return HttpResponseRedirect(reverse('home'))