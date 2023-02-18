"""
Social recipe views
"""
import json
from collections import Counter
from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.views import View
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import RedirectView
from django.db.models import Count, Avg, Q, F, Case, When
from django.contrib import messages
from django.utils.text import slugify
from django.core.paginator import Paginator
from .models import (Recipes, User, StarRating, Ingredients,
                     Comments, RecipeItems, Methods, RecipeImages,
                     UserDetails)
from .forms import (CommentsForm, SearchRecipeForm, FilterRecipeForm,
                    RecipesForm, AddToRecipeForm, RecipeItemsForm,
                    MethodsForm, UserDetailsForm, FollowForm, UnfollowForm,
                    RatingForm, RecipeImagesForm, IngredientsForm)


Recipes_obj = Recipes.objects
StarRating_obj = StarRating.objects
Ingredients_obj = Ingredients.objects
Methods_obj = Methods.objects
RecipeItems_obj = RecipeItems.objects
UserDetails_obj = UserDetails.objects


class HomeList(View):
    """
    The index page view
    """
    def get(self, request):
        '''
        get request
        '''
        top_recipes = Recipes_obj.filter(status=1).annotate(
            favourites_count=Count('favourites')).order_by(
                '-favourites_count')[:3]
        top_recipes = get_average_rating(top_recipes)
        return render(
            request,
            "index.html",
            {
                "top_users": top_recipes,
                "page_name": "Home",
            }
        )


def recipe_filter_list(search_list):
    '''
    return all recipes with the name contains search_list
    '''
    temp_recipes_list = Recipes_obj.filter(status=1)
    for i in search_list:
        temp_recipes_list = temp_recipes_list.filter(
            Q(recipe_items__ingredients__name__icontains=i.name))
    return temp_recipes_list


def get_average_rating(recipes_list):
    '''
    gives each recipe a average rating
    '''
    for arecipe in recipes_list:
        recipes_count = StarRating_obj.filter(recipe=arecipe).count()
        recipes_avg = StarRating.get_average(arecipe.id)
        arecipe.the_star_rating = recipes_avg
        arecipe.the_star_rating_int = range(0, int(recipes_avg or 0))
        arecipe.the_star_rating_count = recipes_count
    return recipes_list


def following_change(request, username):
    '''
    will toggle the state of following
    '''
    user_details = request.user.user_details
    follow_form = FollowForm(request.POST)
    unfollow_form = UnfollowForm(request.POST)
    page_name = get_object_or_404(User, username=username)
    if 'follow' in request.POST:
        if follow_form.is_valid():
            request.user.user_details.follows.add(page_name)
            user_details.save()
            messages.success(request, 'Following')
        else:
            errors = follow_form.errors.as_data()
            error_message = ""
            for key, value in errors.items():
                error_message += f"{key}: {value[0].message}\n"
            messages.error(request, f"Error Follow: {error_message}")
    elif 'unfollow' in request.POST:
        if unfollow_form.is_valid():
            request.user.user_details.follows.remove(page_name)
            user_details.save()
            messages.success(request, ' Unfollowing')
        else:
            messages.error(request, 'Error Unfollowing')


def paginate_recipes(request, recipes):
    '''
    will paginate the recipes
    '''
    paginate_by = 6
    page = request.GET.get('page') or 1
    paginator = Paginator(recipes, paginate_by)
    paginator = paginator.get_page(page)
    return paginator


class RecipesList(View):
    '''
    the list for recipes for recipes page
    '''
    def sort_functions(self, recipes_list, kwargs):
        '''
        will run the sort for the recipes
        '''
        if 'sort_type' in kwargs:
            sort_name = kwargs['sort_type']
            if sort_name == "name":
                sort_name = "A"
                recipes_list = recipes_list.order_by('title')
            elif sort_name == "rating":
                sort_name = "B"
                recipes_list = recipes_list.annotate(
                    average_rating=Avg(
                        'star_rating__rating')).order_by(
                            Case(
                                When(
                                    average_rating__isnull=True,
                                    then=1), default=0), '-average_rating')
            elif sort_name == "favourite":
                sort_name = "C"
                recipes_list = recipes_list.annotate(
                    num_favorites=Count(
                        'favourites')).order_by('-num_favorites')
            elif sort_name == "date":
                sort_name = "D"
                recipes_list = recipes_list.order_by('-upload_date')
            elif sort_name == "time":
                sort_name = "E"
                recipes_list = recipes_list.annotate(
                    total_time=F(
                        'prep_time')+F(
                            'cook_time')).order_by('total_time')
        return recipes_list
    
    def top_5_ingredients(self):
        '''
        get the most common ingredients
        '''
        ingredients_list = RecipeItems.objects.values_list('ingredients__name', flat=True)
        top_ingredients = Counter(ingredients_list).most_common(5)
        return top_ingredients

    def get(self, request, **kwargs):
        '''
        get request for recipe page
        '''
        recipes_list = Recipes_obj.filter(
            status=1).order_by('-upload_date')
        form = SearchRecipeForm(request.GET)
        filter_form = FilterRecipeForm(request.GET)
        query = True
        if form.is_valid():
            if form.cleaned_data['search_query'] != "":
                recipes_list = form.cleaned_data['search_query']
                recipes_list = Recipes_obj.filter(
                    status=1).filter(Q(
                        author__username__icontains=recipes_list) | Q(
                            title__icontains=recipes_list)).order_by(
                                '-upload_date')
        recipe_elm = []
        if filter_form.is_valid():
            recipe_elm = filter_form.cleaned_data['filter_query']
            recipes_list = recipe_filter_list(recipe_elm)
        recipes_list = self.sort_functions(recipes_list, kwargs)
        recipes_list = get_average_rating(recipes_list)
        recipes_list = paginate_recipes(request, recipes_list)
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
                "top_ingredients": self.top_5_ingredients(),
            }
        )


class RecipeDetail(View):
    """
    the view for the single recipe page
    """
    def get(self, request, slug):
        '''
        get request for single recipe page
        '''
        queryset = Recipes_obj
        rated = False
        recipe = get_object_or_404(queryset, slug=slug)
        if recipe.status == 1 or request.user == recipe.author:
            recipe_methods = recipe.methods.order_by('order')
            recipe_comments = recipe.comments.order_by('-post_date')
            recipe_ingredients = recipe.recipe_items.filter()
            recipe_images = recipe.recipe_images.filter()
            recipes_avg = StarRating_obj.filter(
                recipe=recipe).aggregate(Avg('rating')).get('rating__avg')
            recipes_count = StarRating_obj.filter(recipe=recipe).count()
            star_loop = range(0, int(recipes_avg or 0))
            empty_star_loop = range(int(recipes_avg or 0), 5)
            favourited = False
            if recipe.favourites.filter(id=self.request.user.id).exists():
                favourited = True
            if request.user.is_authenticated:
                if StarRating_obj.filter(
                    user=request.user).filter(
                        recipe=recipe).exists():
                    the_rating = StarRating_obj.filter(
                        user=request.user).filter(recipe=recipe).first()
                    star_loop = range(0, int(the_rating.rating))
                    empty_star_loop = range(int(the_rating.rating), 5)
                    rated = True
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
                    "rating_form": RatingForm(),
                    "rated": rated,
                    "image_form": RecipeImagesForm(),
                },
            )
        return HttpResponseRedirect(reverse('home'))

    def delete(self, request, *args, **kwargs):
        '''
        delete comments and images from recipes
        '''
        data = json.loads(request.body)
        model = data.get('model')
        item_id = data.get('id')
        if model == "comment":
            record = get_object_or_404(Comments, id=item_id)
        else:
            record = get_object_or_404(RecipeImages, id=item_id)
            messages.success(request, 'Removed Image')
        record.delete()
        return JsonResponse({"message": item_id}, status=200)

    def post(self, request, slug, *args, **kwargs):
        '''
        post request for single recipe
        '''
        rated = False
        valid_comment = True
        queryset = Recipes_obj.filter(status=1)
        recipe = get_object_or_404(queryset, slug=slug)
        recipe_methods = recipe.methods.order_by('order')
        recipe_comments = recipe.comments.filter(
            status=1).order_by('-post_date')
        recipe_ingredients = recipe.recipe_items.filter()
        recipe_images = recipe.recipe_images.filter()
        recipes_avg = StarRating_obj.filter(
            recipe=recipe).aggregate(Avg('rating')).get('rating__avg')
        recipes_count = StarRating_obj.filter(recipe=recipe).count()
        star_loop = range(0, int(recipes_avg or 0))
        empty_star_loop = range(int(recipes_avg or 0), 5)
        if request.user.is_authenticated:
            if StarRating_obj.filter(user=request.user).filter(
                    recipe=recipe).exists():
                the_rating = StarRating_obj.filter(
                    user=request.user).filter(recipe=recipe).first()
                star_loop = range(0, int(the_rating.rating))
                empty_star_loop = range(int(the_rating.rating), 5)
                rated = True
        favourited = False
        if recipe.favourites.filter(id=self.request.user.id).exists():
            favourited = True
        if 'the_comment_form' in request.POST:
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
        elif 'the_like_form' in request.POST:
            return make_a_like(request, slug)
        elif 'the_rating_form' in request.POST:
            rating_form = RatingForm(data=request.POST)
            if rating_form.is_valid():
                if StarRating_obj.filter(user=request.user).filter(
                        recipe=recipe).exists():
                    the_rating = StarRating_obj.filter(
                        user=request.user).filter(recipe=recipe).first()
                    the_rating.delete()
                rating_form.instance.user = request.user
                rating = rating_form.save(commit=False)
                rating.recipe = recipe
                rating.save()
                messages.success(request, 'Rating Added')
                return JsonResponse({'status': True})
            else:
                messages.error(request, 'Error With Rating')
                return JsonResponse({'status': False})
        elif 'the_image_form' in request.POST:
            image_form = RecipeImagesForm(request.POST, request.FILES)
            if image_form.is_valid():
                image_form.instance.user = request.user
                image = image_form.save(commit=False)
                image.recipe = recipe
                if 'recipe_image' in request.FILES:
                    image.recipe_image = request.FILES['recipe_image']
                image.save()
                messages.success(request, 'Image Added')
                return HttpResponseRedirect(
                    reverse(
                        'recipe_detail',
                        kwargs={'slug': recipe.slug}))
            else:
                messages.error(request, 'Error With Image Upload')

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
                "commented": valid_comment,
                "valid_comment": valid_comment,
                "comment_form": CommentsForm(),
                "recipes_avg": recipes_avg,
                "recipes_count": recipes_count,
                "star_loop": star_loop,
                "empty_star_loop": empty_star_loop,
                "rating_form": RatingForm(),
                "rated": rated,
                "image_form": RecipeImagesForm(),
            },
        )


def make_a_like(request, slug):
    '''
    will toggle the favourites for a recipe
    '''
    recipe = get_object_or_404(Recipes, slug=slug)
    if recipe.favourites.filter(id=request.user.id).exists():
        recipe.favourites.remove(request.user)
        return JsonResponse({'liked': False})
    else:
        recipe.favourites.add(request.user)
    return JsonResponse({'liked': True})


def get_average_recipe_rating(a_user):
    '''
    will get the average rating for a user
    '''
    page_name = get_object_or_404(User, username=a_user)
    recipe = Recipes_obj.filter(author=page_name.id).filter(status=1)
    count = 0
    num_of_ratings = 0
    recipes_avg = []
    total_rec = 0
    for i in recipe:
        recipes_avg.append(StarRating_obj.filter(
            recipe=i).aggregate(Avg('rating')))
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
    '''
    get all the details for the user page
    '''
    page_name = get_object_or_404(User, username=username)
    follow_form = None
    unfollow_form = None
    is_following_data = 0
    if request.user.is_authenticated:
        if page_name.user_follows.filter(user=request.user).exists():
            is_following_data = 2
        else:
            is_following_data = 1
        follow_form = FollowForm()
        unfollow_form = UnfollowForm()
    user_recipe_average = get_average_recipe_rating(username)
    if username == request.user.username:
        showing_recipes = Recipes_obj.filter(
            author=page_name).order_by('title')
    else:
        showing_recipes = Recipes_obj.filter(
            status=1).filter(author=page_name).order_by('title')
    showing_recipes = get_average_rating(showing_recipes)
    fav_recipes = Recipes_obj.filter(favourites=page_name).filter(status=1)
    fav_recipes = get_average_rating(fav_recipes)
    items = {"page_name": page_name,
             "fav_recipes_count": len(fav_recipes),
             "is_following": is_following_data,
             "average_recipe": user_recipe_average,
             "fav_recipes": fav_recipes,
             "showing_recipes": showing_recipes,
             "follow_form": follow_form,
             "unfollow_form": unfollow_form, }
    return items


class ProfilePage(View):
    """
    The users profile page
    """
    def get(self, request, username, *args, **kwargs):
        '''
        the get request
        '''
        user_form = None
        follow_form = None
        unfollow_form = None
        if request.user.is_authenticated:
            user_details = request.user.user_details
            user_form = UserDetailsForm(instance=user_details)
            follow_form = FollowForm()
            unfollow_form = UnfollowForm()
        p_details = profile_details(self.request, username)
        p_details.update({
                "logged_in_user": request.user.username,
                "user_form": user_form,
                "follow_form": follow_form,
                "unfollow_form": unfollow_form,
        })
        return render(
            request,
            "user_profile_page.html",
            p_details
        )

    def post(self, request, username, *args, **kwargs):
        '''
        the post request
        '''
        user_details = request.user.user_details
        user_form = UserDetailsForm(
            request.POST, request.FILES, instance=user_details)
        if 'follow' in request.POST or 'unfollow' in request.POST:
            following_change(request, username)
        elif user_form.is_valid():
            user_form.save()
        return redirect('profile_page', username=username)


class Profilerecipes(View):
    """
    the user recipes page
    """
    def get(self, request, username, *args, **kwargs):
        '''
        the get request
        '''
        the_name = get_object_or_404(User, username=username)
        p_details = profile_details(self.request, username)
        p_details.update({"logged_in_user": the_name, })
        if username != request.user.username:
            recipes = Recipes_obj.filter(
                status=1).filter(author=the_name).order_by('title')
        else:
            recipes = Recipes_obj.filter(author=the_name).order_by('title')
        recipes = get_average_rating(recipes)
        recipes_len = len(recipes)
        recipes = paginate_recipes(request, recipes)

        p_details.update({
            "recipe_list": recipes,
            "recipe_list_count": recipes_len, })
        return render(
            request,
            "user_recipes.html",
            p_details
        )

    def post(self, request, username, *args, **kwargs):
        '''
        the post request
        '''
        if 'follow' in request.POST or 'unfollow' in request.POST:
            following_change(request, username)
        return redirect('profile_page_recipes', username=username)


class ProfileRecipesAdd(View):
    """
    the user recipes add recipe page
    """
    def get(self, request, username, *args, **kwargs):
        '''
        the get request
        '''
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
        '''
        the post request
        '''
        if username == request.user.username:
            recipe_form = RecipesForm(data=request.POST, files=request.FILES)
            if recipe_form.is_valid():
                recipe_form.instance.author = request.user
                title = recipe_form.cleaned_data['title']
                slug = slugify(title)
                if recipe_form.cleaned_data['publish'] is True:
                    recipe_form.instance.status = 1
                recipe = recipe_form.save(commit=False)
                recipe.slug = slug
                if 'recipe_image' in request.FILES:
                    recipe.recipe_image = request.FILES['recipe_image']
                recipe.save()
                user_profile = UserDetails_obj.get(user=request.user)
                user_profile.update_status()
                user_profile.save()
                messages.success(request, 'Recipe Added')
                valid_recipe = True
            else:
                recipe_form = RecipesForm()
                messages.error(request, 'Error With Recipe')
                valid_recipe = False

            p_details = profile_details(self.request, username)
            p_details.update({"logged_in_user": request.user,
                              "add_form": recipe_form})

            if valid_recipe is False:
                return render(
                    request,
                    "user_recipes_add.html",
                    p_details
                )
            else:
                return HttpResponseRedirect(
                        reverse(
                            'profile_page_recipes_edit',
                            kwargs={
                                'username': username,
                                'recipe': recipe.slug}))
        else:
            if request.user.is_authenticated:
                return HttpResponseRedirect(
                    reverse(
                        'profile_page',
                        kwargs={'username': request.user.username}))
            return HttpResponseRedirect(reverse('home'))


class ProfileRecipesEdit(View):
    """
    the user recipes edit recipe page
    """
    form_class = AddToRecipeForm
    paginate_by = 10  # Show 10 ingredients per page

    def ingredient_paginate(self, request, search_term):
        '''
        will paginate the ingredients in the search results
        '''
        go_to_id_id = None
        page = request.GET.get('page') or 1
        ingredients = Ingredients_obj.filter()
        if page != 1:
            go_to_id_id = 'ingredients_section'
        if search_term:
            ingredients = ingredients.filter(name__icontains=search_term)
            go_to_id_id = 'ingredients_section'
        paginator = Paginator(ingredients, self.paginate_by)
        paginator = paginator.get_page(page)
        return {'paginator': paginator,
                'results_count': len(ingredients),
                'go_to_id_id': go_to_id_id}

    def get(self, request, username, recipe, *args, **kwargs):
        '''
        the get request
        '''
        if username == request.user.username:
            the_recipe = get_object_or_404(Recipes, slug=recipe)
            form = self.form_class(request.GET)
            add_ingredients_form = RecipeItemsForm()
            edit_form = RecipesForm(instance=the_recipe)
            search_term = form.data.get('search_term')
            recipe_ingredients = the_recipe.recipe_items.filter()
            # Methods
            method_form = MethodsForm()
            the_methods = Methods_obj.filter(
                recipe=the_recipe).order_by('order')
            p_details = profile_details(self.request, username)
            p_details.update(
                self.ingredient_paginate(self.request, search_term))
            p_details.update({"logged_in_user": request.user,
                              'form': form,
                              'i_form': add_ingredients_form,
                              'edit_form': edit_form,
                              'recipe_ingredients': recipe_ingredients,
                              'recipe': the_recipe,
                              'method_form': method_form,
                              'the_methods': the_methods,
                              'ingredients_form': IngredientsForm(),
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
        '''
        the post request
        '''
        if username == request.user.username:
            the_recipe = get_object_or_404(Recipes, slug=recipe)
            recipe_form = RecipesForm(instance=the_recipe)
            if 'the_recipe_form' in request.POST:
                go_to_id_id = None
                recipe_form = RecipesForm(
                    data=request.POST,
                    files=request.FILES,
                    instance=the_recipe)
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
                    return redirect(reverse(
                        'profile_page_recipes_edit',
                        kwargs={
                            'username': recipe.author,
                            'recipe': recipe.slug}),
                        {'go_to_id_id': 'ingredients_section'})
                else:
                    add_ingredients_form = RecipeItemsForm()
                    messages.error(request, 'Error With Recipe')
            elif "the_ingredient_form" in request.POST:
                add_ingredients_form = RecipeItemsForm(data=request.POST)
                go_to_id_id = 'ingredients_section'
                if add_ingredients_form.is_valid():
                    ing = add_ingredients_form.instance.ingredients
                    if RecipeItems_obj.filter(
                            recipe=the_recipe,
                            ingredients=ing):
                        item_id = RecipeItems_obj.filter(
                            recipe=the_recipe, ingredients=ing
                            ).values('id').first()['id']
                        record = get_object_or_404(RecipeItems, id=item_id)
                        record.delete()
                        add_ingredients_form.instance.recipe = the_recipe
                        recipe_item = add_ingredients_form.save(commit=False)
                        recipe_item.save()
                        messages.warning(request, 'Ingredient Amount Updated')
                    else:
                        add_ingredients_form.instance.recipe = the_recipe
                        recipe_item = add_ingredients_form.save(commit=False)
                        recipe_item.save()
                        messages.success(request, 'Ingredient Added')
                else:
                    add_ingredients_form = RecipeItemsForm()
                    messages.error(request, 'Error With Ingredient')

            elif ("the_method_form" in request.POST and
                  "the_method_form_id" not in request.POST):
                add_methods_form = MethodsForm(data=request.POST)
                go_to_id_id = 'method_section_area'
                if add_methods_form.is_valid():
                    add_methods_form.instance.recipe = the_recipe
                    add_methods_form.instance.order = \
                        Methods.number_of_methods(self, the_recipe.id)+1
                    method_item = add_methods_form.save(commit=False)
                    method_item.save()
                    messages.success(request, 'Method Added')
            elif "the_method_form_id" in request.POST:
                add_methods_form = MethodsForm(data=request.POST)
                go_to_id_id = 'method_section_area'
                if add_methods_form.is_valid():
                    method_id = add_methods_form.data.get('the_method_form_id')
                    method_instance = Methods_obj.get(id=method_id)
                    method_instance.method = \
                        add_methods_form.cleaned_data['method']
                    method_instance.save()
                    messages.success(request, 'Method Updated')
            elif "the_delete_form" in request.POST:
                item_id = request.POST.get('id')
                record = get_object_or_404(Recipes, id=item_id)
                record.delete()
                return redirect(
                    reverse(
                        'profile_page_recipes',
                        kwargs={'username': request.user.username}))
            elif "the_ingredients_form" in request.POST:
                the_form = IngredientsForm(data=request.POST)
                go_to_id_id = 'ingredients_section'
                if the_form.is_valid():
                    item = the_form.save(commit=False)
                    item.save()
                    messages.success(request, 'Ingredient Added')
            # Methods
            method_form = MethodsForm()
            the_methods = Methods_obj.filter(
                recipe=the_recipe).order_by('order')
            form = self.form_class(request.GET)
            add_ingredients_form = RecipeItemsForm()
            search_term = form.data.get('search_term')
            recipe_ingredients = the_recipe.recipe_items.filter()
            p_details = profile_details(self.request, username)
            p_details.update(self.ingredient_paginate(
                self.request,
                search_term,))
            p_details.update({"logged_in_user": request.user,
                              'form': form,
                              'i_form': add_ingredients_form,
                              'edit_form': recipe_form,
                              'recipe_ingredients': recipe_ingredients,
                              'recipe': the_recipe,
                              'go_to_id_id': go_to_id_id,
                              'method_form': method_form,
                              'the_methods': the_methods,
                              'ingredients_form': IngredientsForm(),
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

    def delete(self, request, *args, **kwargs):
        '''
        delete method
        '''
        last = 0
        data = json.loads(request.body)
        item_id = data.get('id')
        model = data.get('model')
        if model == 'RecipeItems':
            record = get_object_or_404(RecipeItems, id=item_id)
            record.delete()
        elif model == 'Methods':
            record = get_object_or_404(Methods, id=item_id)
            temp_record = record
            record.delete()
            if Methods_obj.filter(recipe=temp_record.recipe).exists():
                last = 1
        return JsonResponse({"message": item_id, "last": last}, status=200)


class ProfileFollowers(View):
    """
    the user following page
    """
    def get(self, request, username, *args, **kwargs):
        '''
        get method
        '''
        page_name = get_object_or_404(User, username=username)
        followers_w_rating = \
            page_name.user_details.get_followers().all().order_by('username')
        p_details = profile_details(self.request, username)
        for follow in followers_w_rating:
            follow.average_rating = get_average_recipe_rating(follow.username)
            follow.is_following_data = 0
            if request.user.is_authenticated:
                if follow.user_follows.filter(user=request.user).exists():
                    follow.is_following_data = 2
                else:
                    follow.is_following_data = 1

        p_details.update({
            "logged_in_user": request.user,
            "user_follow_rating": followers_w_rating})
        return render(
            request,
            "user_followers.html",
            p_details
        )

    def post(self, request, username, *args, **kwargs):
        '''
        post method
        '''
        if 'follow' in request.POST or 'unfollow' in request.POST:
            the_username = username
            if 'the_follow_form' in request.POST:
                the_username = request.POST['the_follow_form']
            following_change(request, the_username)
        return redirect('profile_page_followers', username=username)


class ProfileFavourites(View):
    """
    the user recipes Favourites recipe page
    """
    def get(self, request, username, *args, **kwargs):
        '''
        get method
        '''
        page_name = get_object_or_404(User, username=username)
        fav_recipes = Recipes_obj.filter(favourites=page_name).filter(status=1)
        fav_recipes = get_average_rating(fav_recipes)
        fav_recipes = paginate_recipes(request, fav_recipes)

        p_details = profile_details(self.request, username)
        p_details.update({"logged_in_user": request.user, })
        p_details.update({"recipe_list": fav_recipes, })
        return render(
            request,
            "user_favourites.html",
            p_details
        )

    def post(self, request, username, *args, **kwargs):
        '''
        post method
        '''
        if 'follow' in request.POST or 'unfollow' in request.POST:
            following_change(request, username)
        return redirect('profile_page_favourites', username=username)


class AboutUs(View):
    """
    The about us page for whats cooking
    """
    def get(self, request):
        '''
        get method
        '''
        return render(
            request,
            "about_us.html",
            {
                "page_name": "About Us",
            }
        )
    
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        model = data.get('status')
        if model == 1:
            messages.success(request, 'Message Sent')
        else:
            messages.error(request, 'Error With Message')
        return JsonResponse({"message": "Message"}, status=200)


class CurrentUserProfileRedirectView(LoginRequiredMixin, RedirectView):
    """
    redirect for user logging in
    """
    def get_redirect_url(self, *args, **kwargs):
        return reverse(
            'profile_page',
            kwargs={'username': self.request.user.username})
