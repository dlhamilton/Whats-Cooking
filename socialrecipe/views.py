# from itertools import chain
from django.shortcuts import render, get_object_or_404, reverse,redirect
from django.views import generic, View
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import RedirectView
from .models import Recipes, User, UserDetails, ShoppingList, StarRating, Ingredients, Comments, RecipeItems, Methods
from .forms import CommentsForm, SearchRecipeForm, FilterRecipeForm, RecipesForm, AddToRecipeForm, RecipeItemsForm, MethodsForm, UserDetailsForm
from django.db.models import Count, Avg, Q, F, Case, When
from django.urls import resolve
from django.template import loader
from django.contrib import messages
import json
from django.utils.text import slugify
from django.core.paginator import Paginator
from cloudinary.forms import cl_init_js_callbacks


class HomeList(View):
    def get(self, request, *args, **kwargs):
        top_recipes = Recipes.objects.filter(status=1).annotate(favourites_count=Count('favourites')).order_by('-favourites_count')[:3]
        top_recipes = get_average_rating(top_recipes)
        return render(
            request,
            "index.html",
            {
                # "top_recipes": top_recipes,
                "top_users": top_recipes,
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
    test = []
    # for i in search_list:
        # test.append(i.name)
    temp_recipes_list = Recipes.objects.filter(status=1)
    for i in search_list:
        temp_recipes_list = temp_recipes_list.filter(Q(recipe_items__ingredients__name__icontains=i.name))
        # test.append(recipes_list)
    
    return temp_recipes_list


def get_average_rating(recipes_list):
    for arecipe in recipes_list:
        recipes_count = StarRating.objects.filter(recipe=arecipe).count()
        recipes_avg = StarRating.get_average(arecipe.id)
        arecipe.the_star_rating = recipes_avg
        arecipe.the_star_rating_int = range(0, int(recipes_avg or 0))
        arecipe.the_star_rating_count = recipes_count
    return recipes_list


def paginate_recipes(request, recipes):
    paginate_by = 6
    page = request.GET.get('page') or 1
    paginator = Paginator(recipes, paginate_by)
    paginator = paginator.get_page(page)
    return paginator


class RecipesList(View):

    def sort_functions(self, recipes_list, kwargs):
        if 'sort_type' in kwargs:
            sort_name = kwargs['sort_type']
            if sort_name == "name":
                sort_name = "A"
                recipes_list = recipes_list.order_by('title')
            elif sort_name == "rating":
                sort_name = "B"
                recipes_list = recipes_list.annotate(average_rating=Avg('star_rating__rating')).order_by(Case(When(average_rating__isnull=True, then=1), default=0),'-average_rating')
            elif sort_name == "favourite":
                sort_name = "C"
                recipes_list = recipes_list.annotate(num_favorites=Count('favourites')).order_by('-num_favorites')
            elif sort_name == "date":
                sort_name = "D"
                recipes_list = recipes_list.order_by('-upload_date')
            elif sort_name == "time":
                sort_name = "E"
                recipes_list = recipes_list.annotate(total_time=F('prep_time')+F('cook_time')).order_by('total_time')
        return recipes_list

    def get(self, request, *args, **kwargs):
        recipes_list = Recipes.objects.filter(status=1).order_by('-upload_date')
        form = SearchRecipeForm(request.GET)
        filter_form = FilterRecipeForm(request.GET)
        query = True
        if form.is_valid():
            if form.cleaned_data['search_query'] != "": 
                recipes_list = form.cleaned_data['search_query']
                recipes_list = Recipes.objects.filter(status=1).filter(Q(author__username__icontains=recipes_list) | Q(title__icontains=recipes_list)).order_by('-upload_date')
        recipe_elm = []
        if filter_form.is_valid():
            recipe_elm = filter_form.cleaned_data['filter_query']
            recipes_list = RecipeFilterList(recipe_elm)
        recipes_list = self.sort_functions(recipes_list, kwargs)
        recipes_list = get_average_rating(recipes_list)
        recipes_list = paginate_recipes(request,recipes_list)
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
                "searched_ingri_list": recipe_elm,
            }
        )


class RecipeDetail(View):
    def get(self, request, slug, *args, **kwargs):
        queryset = Recipes.objects
        recipe = get_object_or_404(queryset, slug=slug)
        if recipe.status == 1 or request.user == recipe.author:
            recipe_methods = recipe.methods.order_by('order')
            recipe_comments = recipe.comments.order_by('-post_date')
            recipe_ingredients = recipe.recipe_items.filter()
            recipe_images = recipe.recipe_images.filter()
            recipes_avg = StarRating.objects.filter(recipe=recipe).aggregate(Avg('rating')).get('rating__avg')
            recipes_count = StarRating.objects.filter(recipe=recipe).count()
            star_loop = range(0, int(recipes_avg or 0))
            empty_star_loop = range(0, 5-int(recipes_avg or 0))
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

    def delete(self, request, *args, **kwargs):
        data = json.loads(request.body)
        id = data.get('id')
        record = get_object_or_404(Comments, id=id)
        record.delete()
        return JsonResponse({"message": id}, status=200)

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
            messages.success(request, 'Comment Added')
            valid_comment = True
        else:
            comment_form = CommentsForm()
            messages.error(request, 'Error With Comment')
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
    num_of_ratings = 0
    recipes_avg = []
    total_rec = 0
    for i in recipe:
        recipes_avg.append(StarRating.objects.filter(recipe=i).aggregate(Avg('rating')))      
        if recipes_avg[count].get('rating__avg') is not None:
            total_rec = total_rec + recipes_avg[count].get('rating__avg')
            num_of_ratings += 1
        count = count+1
    if num_of_ratings != 0:
        user_recipe_average = total_rec/num_of_ratings
    else:
        user_recipe_average = 0
    thisdict = { 
        "user_recipe_average": user_recipe_average,
        "user_recipe_average_star": range(0, int(user_recipe_average)),
        "user_recipe_average_blank": range(0, 5-int(user_recipe_average)),
    }
    return thisdict


def profile_details(request, username):
    page_name = get_object_or_404(User, username=username)

    is_following_data = 0
    if request.user.is_authenticated:
        if page_name.user_follows.filter(user=request.user).exists():
            is_following_data = 2
        else:
            is_following_data = 1

    user_recipe_average = getAverageRecipeRating(username)

    if username == request.user.username:
        showing_recipes = Recipes.objects.filter(author=page_name).order_by('title')
    else:
        showing_recipes = Recipes.objects.filter(status=1).filter(author=page_name).order_by('title')
    showing_recipes = get_average_rating(showing_recipes)
    
    fav_recipes = []
    all_recipes = Recipes.objects.filter(status=1)
    for r in all_recipes:
        if r.favourites.filter(id=page_name.id).exists():
            fav_recipes.append(r)
    fav_recipes = get_average_rating(fav_recipes)
    items = {"page_name": page_name,
             "fav_recipes_count": len(fav_recipes),
             "is_following": is_following_data,
             "average_recipe": user_recipe_average,
             "fav_recipes": fav_recipes,
             "showing_recipes": showing_recipes, }
    return items


class ProfilePage(View):

    def get(self, request, username, *args, **kwargs):
        user_form = None
        if request.user.is_authenticated:
            user_details = request.user.user_details
            user_form = UserDetailsForm(instance=user_details)
        p_details = profile_details(self.request, username)
        p_details.update({
                "logged_in_user": request.user.username,
                "user_form": user_form,
        })
        return render(
            request,
            "user_profile_page.html",
            p_details
        )

    def post(self, request, username, *args, **kwargs):
        user_details = request.user.user_details
        user_form = UserDetailsForm(request.POST, request.FILES, instance=user_details)
        if user_form.is_valid():
            user_form.save()
            return redirect('profile_page', username=username)


class ProfileShoppingList(View):
    def get(self, request, username, *args, **kwargs):
        if username == request.user.username:
            p_details = profile_details(self.request, username)
            p_details.update({"logged_in_user": request.user, })
            return render(
                request,
                "shopping_lists.html",
                p_details)
        else:
            if request.user.is_authenticated:
                return HttpResponseRedirect(
                    reverse('profile_page',
                            kwargs={'username': request.user.username}))
            return HttpResponseRedirect(reverse('home'))


class ProfileSingleList(View):
    def get(self, request, username, list, *args, **kwargs):
        if username == request.user.username:
            shopping_list = get_object_or_404(ShoppingList, slug=list)
            user_list_items = shopping_list.shopping_list_items.filter()
            p_details = profile_details(self.request, username)
            p_details.update({
                    "logged_in_user": request.user,
                    "user_list": user_list_items,
                    "user_shopping_list": shopping_list,
            })
            return render(
                request,
                "shopping_list.html",
                p_details
            )
        else:
            if request.user.is_authenticated:
                return HttpResponseRedirect(
                    reverse(
                        'profile_page',
                        kwargs={'username': request.user.username}))
            return HttpResponseRedirect(reverse('home'))


class Profilerecipes(View):
    def get(self, request, username, *args, **kwargs):
        p_details = profile_details(self.request, username)
        p_details.update({"logged_in_user": request.user, })
        return render(
            request,
            "user_recipes.html",
            p_details
        )


class ProfileRecipesAdd(View):
    def get(self, request, username, *args, **kwargs):
        if username == request.user.username:

            p_details = profile_details(self.request, username)
            p_details.update({"logged_in_user": request.user,
                              "add_form": RecipesForm()})
            return render(
                request,
                "user_recipes_add.html",
                p_details
            )
        else:
            if request.user.is_authenticated:
                return HttpResponseRedirect(
                    reverse(
                        'profile_page',
                        kwargs={'username': request.user.username}))
            return HttpResponseRedirect(reverse('home'))

    def post(self, request, username, *args, **kwargs):
        if username == request.user.username:

            recipe_form = RecipesForm(data=request.POST, files=request.FILES)
            if recipe_form.is_valid():

                recipe_form.instance.author = request.user

                title = recipe_form.cleaned_data['title']
                
                slug = slugify(title)

                if recipe_form.cleaned_data['publish'] == True:
                    recipe_form.instance.status = 1
                recipe = recipe_form.save(commit=False)
                recipe.slug = slug
                if 'recipe_image' in request.FILES:
                    recipe.recipe_image = request.FILES['recipe_image']
                recipe.save()
                messages.success(request, 'Recipe Added')
                valid_recipe = True
            else:
                recipe_form = RecipesForm()
                messages.error(request, 'Error With Recipe')
                valid_recipe = False

            p_details = profile_details(self.request, username)
            p_details.update({"logged_in_user": request.user,
                              "add_form": recipe_form})

            if valid_recipe == False:
                return render(
                    request,
                    "user_recipes_add.html",
                    p_details
                )
            else:
                return HttpResponseRedirect(
                        reverse(
                            'profile_page_recipes_edit',
                            kwargs={'username':username, 'recipe': recipe.slug}))
        else:
            if request.user.is_authenticated:
                return HttpResponseRedirect(
                    reverse(
                        'profile_page',
                        kwargs={'username': request.user.username}))
            return HttpResponseRedirect(reverse('home'))


class ProfileRecipesEdit(View):
    form_class = AddToRecipeForm
    paginate_by = 10  # Show 10 ingredients per page

    def ingredientPaginate(self,request, search_term):
        go_to_id_id = None
        page = request.GET.get('page') or 1
        ingredients = Ingredients.objects.filter(approved=True)
        if page != 1:
            go_to_id_id = 'ingredients_section'
        if search_term:
            ingredients = ingredients.filter(name__icontains=search_term)
            go_to_id_id = 'ingredients_section'
        paginator = Paginator(ingredients, self.paginate_by)
        paginator = paginator.get_page(page)
        return {'paginator': paginator,
                'results_count': len(ingredients),
                'go_to_id_id': go_to_id_id }

    def get(self, request, username, recipe, *args, **kwargs):
        if username == request.user.username:
            the_recipe = get_object_or_404(Recipes,slug=recipe)
            form = self.form_class(request.GET)
            add_ingredients_form = RecipeItemsForm()
            edit_form = RecipesForm(instance=the_recipe)
            search_term = form.data.get('search_term')
            recipe_ingredients = the_recipe.recipe_items.filter()
            # Methods
            method_form = MethodsForm()
            the_methods = Methods.objects.filter(recipe=the_recipe).order_by('order')

            p_details = profile_details(self.request, username)
            p_details.update(self.ingredientPaginate(self.request, search_term))
            p_details.update({"logged_in_user": request.user,
                              'form': form,
                              'i_form': add_ingredients_form,
                              'edit_form': edit_form,
                              'recipe_ingredients': recipe_ingredients,
                              'recipe': the_recipe,
                              'method_form': method_form,
                              'the_methods': the_methods,
                              })
            return render(
                request,
                "user_recipes_edit.html",
                p_details
            )
        else:
            if request.user.is_authenticated:
                return HttpResponseRedirect(
                    reverse(
                        'profile_page',
                        kwargs={'username': request.user.username}))
            return HttpResponseRedirect(reverse('home'))

    def post(self, request, username, recipe, *args, **kwargs):
        if username == request.user.username:
            
            the_recipe = get_object_or_404(Recipes, slug=recipe)
            recipe_form = RecipesForm(instance=the_recipe)
            if 'the_recipe_form' in request.POST:
                go_to_id_id = None
                recipe_form = RecipesForm(data=request.POST, files=request.FILES, instance=the_recipe)
                if recipe_form.is_valid():

                    recipe_form.instance.author = request.user

                    title = recipe_form.cleaned_data['title']
                    
                    slug = slugify(title)

                    if recipe_form.cleaned_data['publish'] is True:
                        recipe_form.instance.status = 1
                    else:
                        recipe_form.instance.status = 0
                    recipe = recipe_form.save(commit=False)
                    recipe.slug = slug
                    if 'recipe_image' in request.FILES:
                        recipe.recipe_image = request.FILES['recipe_image']
                    recipe.save()
                    messages.success(request, 'Recipe Updated')
                    return redirect(reverse('profile_page_recipes_edit', kwargs={'username':recipe.author, 'recipe': recipe.slug}), {'go_to_id_id': 'ingredients_section'})
                else:
                    add_ingredients_form = RecipeItemsForm()
                    # recipe_form = RecipesForm(instance=the_recipe)
                    messages.error(request, 'Error With Recipe')
            elif "the_ingredient_form" in request.POST:
                add_ingredients_form = RecipeItemsForm(data=request.POST)
                go_to_id_id = 'ingredients_section'
                # context = {'go_to_id_id': go_to_id_id}
                if add_ingredients_form.is_valid():
                    # recipe_form = RecipesForm(instance=the_recipe)
                    if RecipeItems.objects.filter(recipe=the_recipe,
                                                ingredients=add_ingredients_form.instance.ingredients):
                        
                        id = RecipeItems.objects.filter(recipe=the_recipe,ingredients=add_ingredients_form.instance.ingredients).values('id').first()['id']
                        record = get_object_or_404(RecipeItems, id=id)
                        record.delete()

                        add_ingredients_form.instance.recipe = the_recipe
                        
                        recipe_item = add_ingredients_form.save(commit=False)
                        recipe_item.save()
                        messages.warning(request, 'Ingredient Amount Updated')
                        # return redirect(reverse('profile_page_recipes_edit', kwargs={'username':the_recipe.author, 'recipe': the_recipe.slug}), context)
                    else:
                        add_ingredients_form.instance.recipe = the_recipe
                        # add_ingredients_form.instance.ingredients = the_ingredient
                        recipe_item = add_ingredients_form.save(commit=False)
                        recipe_item.save()
                        messages.success(request, 'Ingredient Added')
                        # return redirect(reverse('profile_page_recipes_edit', kwargs={'username':the_recipe.author, 'recipe': the_recipe.slug}), context)
                else:
                    add_ingredients_form = RecipeItemsForm()
                    # recipe_form = RecipesForm(instance=the_recipe)
                    messages.error(request, 'Error With Ingredient')

            elif "the_method_form" in request.POST and not "the_method_form_id" in request.POST:
                add_methods_form = MethodsForm(data=request.POST)
                go_to_id_id = 'method_section_area'
                if add_methods_form.is_valid():
                    add_methods_form.instance.recipe = the_recipe
                    add_methods_form.instance.order = Methods.number_of_methods(self,the_recipe.id)+1
                    method_item = add_methods_form.save(commit=False)
                    method_item.save()
                    messages.success(request, 'Method Added')
            
            elif "the_method_form_id" in request.POST:
                add_methods_form = MethodsForm(data=request.POST)
                go_to_id_id = 'method_section_area'
                if add_methods_form.is_valid():
                    method_id = add_methods_form.data.get('the_method_form_id')
                    method_instance = Methods.objects.get(id=method_id)
                    method_instance.method = add_methods_form.cleaned_data['method']
                    method_instance.save()
                    messages.success(request, 'Method Updated')
            # Methods
            method_form = MethodsForm()
            the_methods = Methods.objects.filter(recipe=the_recipe).order_by('order')

            form = self.form_class(request.GET)
            add_ingredients_form = RecipeItemsForm()
            search_term = form.data.get('search_term')
            recipe_ingredients = the_recipe.recipe_items.filter()
            p_details = profile_details(self.request, username)
            p_details.update(self.ingredientPaginate(self.request, search_term,))
            p_details.update({"logged_in_user": request.user,
                              'form': form,
                              'i_form': add_ingredients_form,
                              'edit_form': recipe_form,
                              'recipe_ingredients': recipe_ingredients,
                              'recipe': the_recipe,
                              'go_to_id_id': go_to_id_id,
                              'method_form': method_form,
                              'the_methods': the_methods,
                              })
            return render(
                request,
                "user_recipes_edit.html",
                p_details
            )
            # return redirect(reverse('profile_page_recipes_edit', kwargs={'username':the_recipe.author, 'recipe': the_recipe.slug}), p_details)
        else:
            if request.user.is_authenticated:
                return HttpResponseRedirect(
                    reverse(
                        'profile_page',
                        kwargs={'username': request.user.username}))
            return HttpResponseRedirect(reverse('home'))

    def delete(self, request, *args, **kwargs):
        last = 0
        data = json.loads(request.body)
        id = data.get('id')
        model = data.get('model')
        if model == 'RecipeItems':
            record = get_object_or_404(RecipeItems, id=id)
            record.delete()
        elif model == 'Methods':
            record = get_object_or_404(Methods, id=id)
            temp_record = record
            record.delete()
            if Methods.objects.filter(recipe=temp_record.recipe).exists():
                last = 1
        return JsonResponse({"message": id, "last": last}, status=200)

    # def put(self, request, *args, **kwargs):
    #     data = json.loads(request.body)
    #     id = data.get('id')
    #     edit_methods_form = MethodsForm(data=request.PUT)
    #     if edit_methods_form.is_valid():
    #         method_instance = Methods.objects.get(id=id)
    #         self.get(request, username, recipe)
    #     else:
    #         self.get(request, username, recipe)


class ProfileFollowers(View):
    def get(self, request, username, *args, **kwargs):
        p_details = profile_details(self.request, username)
        p_details.update({"logged_in_user": request.user, })
        return render(
            request,
            "user_followers.html",
            p_details
        )


class ProfileFavourites(View):
    def get(self, request, username, *args, **kwargs):
        p_details = profile_details(self.request, username)
        p_details.update({"logged_in_user": request.user, })
        return render(
            request,
            "user_favourites.html",
            p_details
        )


class CurrentUserProfileRedirectView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return reverse(
                'profile_page',
                kwargs={'username': self.request.user.username})
        return HttpResponseRedirect(reverse('home'))
