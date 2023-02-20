"""
Testing of Views
"""
import json
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages.storage.fallback import FallbackStorage
from .models import (User, Recipes, UserDetails, StarRating, Units,
                     Ingredients, RecipeItems, Methods)
from .views import (RecipeDetail, CurrentUserProfileRedirectView, RecipesList,
                    RecipeImages, Comments, ProfileRecipesEdit,
                    ProfileRecipesAdd, custom_500, custom_403, custom_404)
from .forms import (RecipeImagesForm)


UserDetails_var = UserDetails.objects
Recipes_var = Recipes.objects
Comments_var = Comments.objects
Methods_var = Methods.objects
StarRating_var = StarRating.objects
Ingredients_var = Ingredients.objects
RecipeImages_var = RecipeImages.objects
Units_var = Units.objects
RecipeItems_var = RecipeItems.objects


class TestHomePage(TestCase):
    """
    Test Home Page View
    """
    def test_get_home_page(self):
        '''
        Test Home Page status
        '''
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')


class TestRecipesList(TestCase):
    """
    Test Recipe Page View
    """
    def setUp(self):
        self.factory = RequestFactory()

        self.user = User.objects.create_user(
            username='testuser', password='testpass')

        self.details = UserDetails_var.create(
            user=self.user,
        )
        self.user.user_details = self.details

        self.recipe = Recipes_var.create(
            title='Test Recipe',
            slug='test_recipe',
            author=self.user,
            status=1,
            upload_date='2022-12-01'
        )
        self.rating = StarRating_var.create(
            rating=3,
            recipe=self.recipe,
            user=self.user
        )
        self.ingredient_1 = Ingredients_var.create(
            name='Tomatoes', approved=True
            )
        self.ingredient_2 = Ingredients_var.create(
            name='Apple', approved=True
            )
        self.unit = Units_var.create(
            name='testunit',
        )
        self.recipeitems = RecipeItems_var.create(
            recipe=self.recipe,
            ingredients=self.ingredient_1,
            amount=2,
            unit=self.unit)

    def test_get(self):
        '''
        Test get for recipe list
        '''
        client = Client()
        response = client.get('/recipes/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes.html')

    def test_get_loggedin(self):
        '''
        Test get for recipe list for logged in user
        '''
        client = Client()
        client.force_login(self.user)
        response = client.get('/recipes/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes.html')

    def test_get_search(self):
        '''
        Test get for recipe list search
        '''
        client = Client()
        response = client.get('/recipes/search/', {'search_query': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes.html')

    def test_get_filter_valid(self):
        '''
        Test get for recipe list filter valid
        '''
        client = Client()
        response = client.get(
            '/recipes/filter/',
            {'filter_query': [self.ingredient_1.pk]})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes.html')
        recipes = Recipes_var.filter(
            recipe_items__ingredients__in=[self.ingredient_1])
        self.assertQuerysetEqual(
            response.context['recipes_list'], [repr(r) for r in recipes])

    def test_get_filter_valid_no_match(self):
        '''
        Test get for recipe list filter valid
        '''
        client = Client()
        response = client.get(
            '/recipes/filter/',
            {'filter_query': [self.ingredient_2.pk]})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes.html')
        self.assertQuerysetEqual(
            response.context['recipes_list'],
            (str(r) for r in 'No Recipes Match Your Search'))
        self.assertEqual(response.context['query'], False)

    def test_get_sort(self):
        '''
        Test get for recipe list sort
        '''
        client = Client()
        response = client.get('/recipes/sort/A')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes.html')

    def test_sort_functions(self):
        '''
        Test get for recipe list sort types
        '''
        view = RecipesList()

        # Test sort by name
        recipes_list = Recipes_var.filter(status=1).order_by(
            '-upload_date')
        sorted_recipes = view.sort_functions(
            recipes_list, {'sort_type': 'name'})
        self.assertEqual(sorted_recipes[0], self.recipe)

        # Test sort by rating
        recipes_list = Recipes_var.filter(status=1).order_by(
            '-upload_date')
        sorted_recipes = view.sort_functions(
            recipes_list, {'sort_type': 'rating'})
        self.assertEqual(sorted_recipes[0], self.recipe)

        # Test sort by favourite
        recipes_list = Recipes_var.filter(status=1).order_by(
            '-upload_date')
        sorted_recipes = view.sort_functions(
            recipes_list, {'sort_type': 'favourite'})
        self.assertEqual(sorted_recipes[0], self.recipe)

        # Test sort by date
        recipes_list = Recipes_var.filter(status=1).order_by(
            '-upload_date')
        sorted_recipes = view.sort_functions(
            recipes_list, {'sort_type': 'date'})
        self.assertEqual(sorted_recipes[0], self.recipe)

        # Test sort by time
        recipes_list = Recipes_var.filter(status=1).order_by(
            '-upload_date')
        sorted_recipes = view.sort_functions(
            recipes_list, {'sort_type': 'time'})
        self.assertEqual(sorted_recipes[0], self.recipe)


class TestRecipeDetail(TestCase):
    """
    Test Single Recipe Page View
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='password'
        )
        self.details = UserDetails_var.create(
            user=self.user,
        )
        self.user.user_details = self.details
        self.details.save()
        self.user.save()

        self.user_authenticated = User.objects.create_user(
            username='testuserauthenticated',
            password='password'
        )
        self.details_authenticated = UserDetails_var.create(
            user=self.user_authenticated,
        )
        self.user_authenticated.user_details = self.details_authenticated
        self.details_authenticated.save()
        self.user_authenticated.save()
        self.recipe = Recipes_var.create(
            title='testrecipe',
            slug='testrecipe',
            author=self.user,
            excerpt='about the recipe',
            status=1,
            recipe_image='',
            prep_time=30,
            cook_time=60,
            serves=4,
        )
        self.recipe_hidden = Recipes_var.create(
            title='recipe_hidden',
            slug='recipe_hidden',
            author=self.user,
            excerpt='about the recipe',
            status=0,
            recipe_image='',
            prep_time=30,
            cook_time=60,
            serves=4
        )
        self.recipe_authenticated = Recipes_var.create(
            title='recipe_authenticated',
            slug='recipe_authenticated',
            author=self.user_authenticated,
            excerpt='about the recipe',
            status=1,
            recipe_image='',
            prep_time=30,
            cook_time=60,
            serves=4
        )
        self.image1 = RecipeImages_var.create(
            recipe_image="path/to/image1.jpg",
            recipe=self.recipe,
            user=self.user,
        )
        self.image2 = RecipeImages_var.create(
            recipe_image="path/to/image2.jpg",
            recipe=self.recipe,
            user=self.user,
        )
        self.comment1 = Comments_var.create(
            body="Comment 1",
            recipe=self.recipe,
            user=self.user,
        )
        self.comment2 = Comments_var.create(
            body="Comment 2",
            recipe=self.recipe,
            user=self.user,
        )
        self.factory = RequestFactory()

    def test_get_recipe_details_with_authenticated_user(self):
        '''
        Test Recipe Page status when user is logged in
        but looking at another user recipe page not hidden
        '''
        client = Client()
        client.force_login(self.user_authenticated)
        response = client.get(f'/recipes/{self.recipe.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipe_detail.html')

    def test_get_recipe_details_with_authenticated_user_hidden(self):
        '''
        Test Recipe Page status when user is logged in
        but looking at another user recipe page hidden
        '''
        client = Client()
        client.force_login(self.user_authenticated)
        response = client.get(f'/recipes/{self.recipe_hidden.slug}/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/')

    def test_get_recipe_details_with_own(self):
        '''
        Test Recipe Page status when user is logged in
        but looking at own recipe page not hidden
        '''
        client = Client()
        client.force_login(self.user)
        response = client.get(f'/recipes/{self.recipe.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipe_detail.html')

    def test_get_recipe_details_with_own_hidden(self):
        '''
        Test Recipe Page status when user is logged in
        but looking at own recipe page hidden
        '''
        client = Client()
        client.force_login(self.user)
        response = self.client.get(f'/recipes/{self.recipe.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipe_detail.html')

    def test_get_recipe_details_with_not_login_user(self):
        '''
        Test Recipe Page status when user is not logged in
        looking at user recipe page hidden
        '''
        response = self.client.get(f'/recipes/{self.recipe_hidden.slug}/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/')

    def test_get_recipe_details_with__user(self):
        '''
        Test Recipe Page status when user is not logged in
        looking at user recipe page not hidden
        '''
        response = self.client.get(f'/recipes/{self.recipe.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipe_detail.html')

    def test_view_shows_correct_recipe(self):
        '''
        Test showing right recipe
        '''
        request = self.factory.get(
            reverse('recipe_detail', args=[self.recipe.slug]))
        request.user = self.user
        response = RecipeDetail.as_view()(request, slug=self.recipe.slug)
        self.assertContains(response, self.recipe.title)

    def test_favourited(self):
        '''
        Test if user has favourited recipe
        '''
        self.recipe.favourites.add(self.user)
        client = Client()
        client.force_login(self.user)
        response = client.get(f'/recipes/{self.recipe.slug}/')
        self.recipe.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['favourited'])

    def test_view_redirects_if_not_author_or_published(self):
        '''
        Test redirect if not your recipe or not published
        '''
        self.recipe.status = 0
        self.recipe.save()
        response = self.client.get(f'/recipes/{self.recipe.slug}/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/')

    def test_view_shows_rated_recipe(self):
        '''
        Test delete of recipe comment
        '''
        StarRating_var.create(user=self.user, recipe=self.recipe, rating=3)
        request = self.factory.get(reverse(
            'recipe_detail', args=[self.recipe.slug]))
        request.user = self.user
        response = RecipeDetail.as_view()(request, slug=self.recipe.slug)
        self.assertEqual(
            response.status_code,
            200
        )
        self.assertTrue(
            StarRating_var.filter(rating=3).exists()
        )

    def test_delete_comment(self):
        '''
        Test delete of recipe comment
        '''
        response = self.client.delete(
            f'/recipes/{self.recipe.slug}/',
            content_type='application/json',
            data=json.dumps({
                "model": "comment",
                "id": self.comment1.id
            })
        )
        self.assertEqual(
            response.status_code,
            200
        )
        self.assertFalse(
            Comments_var.filter(id=self.comment1.id).exists()
        )
        self.assertTrue(
            Comments_var.filter(id=self.comment2.id).exists()
        )

    def test_delete_image(self):
        '''
        Test delete of recipe image
        '''
        response = self.client.delete(
            f'/recipes/{self.recipe.slug}/',
            content_type='application/json',
            data=json.dumps({
                "model": "recipe_images",
                "id": self.image1.id
            })
        )
        self.assertEqual(
            response.status_code,
            200
        )
        self.assertFalse(
            RecipeImages_var.filter(id=self.image1.id).exists()
        )
        self.assertTrue(
            RecipeImages_var.filter(id=self.image2.id).exists()
        )

    def test_delete_nonexistent_record(self):
        '''
        Test delete of recipe image of nonexistent
        '''
        response = self.client.delete(
            f'/recipes/{self.recipe.slug}/',
            content_type='application/json',
            data=json.dumps({
                "model": "recipe_images",
                "id": 999
            })
        )
        self.assertEqual(
            response.status_code,
            404
        )

    def test_post_view_with_comment(self):
        '''
        Test recipe form comment upload
        '''
        client = Client()
        client.force_login(self.user)
        content = {
            'body': 'Test comment',
            'the_comment_form': 'the_comment_form'
            }
        response = client.post(f'/recipes/{self.recipe.slug}/', content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.recipe.comments.count(), 3)
        self.assertTemplateUsed(response, 'recipe_detail.html')

    def test_post_view_with_rating(self):
        '''
        Test recipe rating form
        '''
        client = Client()
        client.force_login(self.user)
        content = {'the_rating_form': 'the_rating_form', 'rating': 4}
        response = client.post(f'/recipes/{self.recipe.slug}/', content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(StarRating_var.count(), 1)

    def test_post_view_with_invalid_rating(self):
        '''
        Test recipe rating form invalid
        '''
        client = Client()
        client.force_login(self.user)
        content = {'the_rating_form': 'the_rating_form'}
        response = client.post(f'/recipes/{self.recipe.slug}/', content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(StarRating_var.count(), 0)
        self.assertDictEqual(
            json.loads(response.content),
            {'status': False})

    def test_post_view_with_rating_update(self):
        '''
        Test recipe rating form update
        '''
        StarRating_var.create(user=self.user, recipe=self.recipe, rating=3)
        client = Client()
        client.force_login(self.user)
        content = {'the_rating_form': 'the_rating_form', 'rating': 4}
        response = client.post(f'/recipes/{self.recipe.slug}/', content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(StarRating_var.count(), 1)
        self.assertEqual(
            StarRating_var.filter(user=self.user).first().rating, 4)

    def test_favourited_post(self):
        '''
        Test if user has favourited recipe
        '''
        self.recipe.favourites.add(self.user)
        client = Client()
        client.force_login(self.user)
        response = client.post(f'/recipes/{self.recipe.slug}/')
        self.recipe.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['favourited'])

    def test_post_view_with_invalid_comment(self):
        '''
        Test recipe form comment upload
        '''
        client = Client()
        client.force_login(self.user)
        content = {
            'the_comment_form': 'the_comment_form'
            }
        response = client.post(f'/recipes/{self.recipe.slug}/', content)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['valid_comment'])
        self.assertEqual(self.recipe.comments.count(), 2)
        self.assertTemplateUsed(response, 'recipe_detail.html')

    def test_post_view_with_like_true(self):
        '''
        Test like form to true
        '''
        client = Client()
        client.force_login(self.user)
        content = {
            'the_like_form': 'the_like_form'
            }
        response = client.post(f'/recipes/{self.recipe.slug}/', content)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            json.loads(response.content),
            {'liked': True})

    def test_post_view_with_like_false(self):
        '''
        Test like form to false
        '''
        self.recipe.favourites.add(self.user)
        client = Client()
        client.force_login(self.user)
        content = {
            'the_like_form': 'the_like_form'
            }
        response = client.post(f'/recipes/{self.recipe.slug}/', content)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            json.loads(response.content),
            {'liked': False})

    def generate_test_image(self):
        '''
        A test image to upload
        '''
        image_path = 'media/test_image.jpg'
        new_photo = SimpleUploadedFile(
            name='test_image.jpg',
            content=open(image_path, 'rb').read(),
            content_type='image/jpeg')
        return new_photo

    def test_post_view_with_image(self):
        '''
        Test recipe form image upload
        '''
        self.assertEqual(RecipeImages_var.count(), 2)
        image = self.generate_test_image()
        form_data = {
            'recipe_image': image,
            'headline': 'This is a test headline',
            'the_image_form': 'the_image_form',
        }
        image_form = RecipeImagesForm(data=form_data, files=form_data)

        self.assertTrue(image_form.is_valid())

        request = self.factory.post(
            reverse('recipe_detail', args=[self.recipe.slug]),
            data=form_data, files=form_data)
        post_data = request.POST.copy()
        post_data.update(form_data)
        request.POST = post_data
        request.FILES.update(form_data)
        request.user = self.user

        # Adding messages to the request
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = RecipeDetail.as_view()(
            request,
            slug=self.recipe.slug,
            format='multipart/form-data',
            data=form_data,
            files=form_data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(RecipeImages_var.count(), 3)
        self.assertEqual(
            RecipeImages_var.last().headline, 'This is a test headline')
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(list(messages)[0]), 'Image Added')

    def test_post_view_with_image_invalid(self):
        '''
        Test recipe form image upload with invalid image
        '''
        image = self.generate_test_image()
        form_data = {
            'recipe_image': image,
            'headline': '',
            'the_image_form': 'the_image_form',
        }
        image_form = RecipeImagesForm(data=form_data, files=form_data)

        self.assertFalse(image_form.is_valid())

        request = self.factory.post(
            reverse('recipe_detail', args=[self.recipe.slug]),
            data=form_data,
            files=form_data)
        post_data = request.POST.copy()
        post_data.update(form_data)
        request.POST = post_data
        request.FILES.update(form_data)
        request.user = self.user

        # Adding messages to the request
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = RecipeDetail.as_view()(
            request,
            slug=self.recipe.slug,
            format='multipart/form-data',
            data=form_data,
            files=form_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(list(messages)[0]), 'Error With Image Upload')


class TestProfilePage(TestCase):
    """
    Test Profile Page View
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='password'
        )
        self.details = UserDetails_var.create(
            user=self.user,
        )
        self.user.user_details = self.details
        self.details.save()
        self.user.save()
        self.user_authenticated = User.objects.create_user(
            username='testuserauthenticated',
            password='password'
        )
        self.details_authenticated = UserDetails_var.create(
            user=self.user_authenticated,
        )
        self.user_authenticated.user_details = self.details_authenticated
        self.details_authenticated.save()
        self.user_authenticated.save()

    def test_get_profile_page(self):
        '''
        Test Profile Page status
        '''
        client = Client()
        client.force_login(self.user)

        response = client.get(f'/users/{self.user.username}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_profile_page.html')

    def test_get_profile_page_loggedin_own(self):
        '''
        Test Profile Page status logged into own profile page
        '''

        client = Client()
        client.force_login(self.user)

        response = client.get(f'/users/{self.user.username}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_profile_page.html')

    def test_get_profile_page_loggedin_else(self):
        '''
        Test Profile Page status when looking at another user logged in
        '''
        client = Client()
        client.force_login(self.user_authenticated)
        response = client.get(f'/users/{self.user.username}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_profile_page.html')

    def test_post_view_with_follow_button(self):
        '''
        Test follow in profile page
        '''
        client = Client()
        client.force_login(self.user)

        response = client.post(f'/users/{self.user.username}/',
                               {'follow': 'follow'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/users/{self.user.username}/')

    def test_post_view_with_unfollow_button(self):
        '''
        Test unfollow in profile page
        '''
        client = Client()
        client.force_login(self.user)

        response = client.post(f'/users/{self.user.username}/',
                               {'unfollow': 'unfollow'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/users/{self.user.username}/')

    def test_post_view_with_valid_form(self):
        '''
        Test valid user detail form
        '''
        client = Client()
        client.force_login(self.user)
        response = client.post(f'/users/{self.user.username}/', {
                'first_name': 'Test',
                'last_name': 'User',
                'location': 'London'
            })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Test')
        self.assertEqual(self.user.last_name, 'User')
        self.assertEqual(response.url, f'/users/{self.user.username}/')

    def test_post_view_with_invalid_form(self):
        '''
        Test invalid user detail form
        '''
        client = Client()
        client.force_login(self.user)
        response = client.post(f'/users/{self.user.username}/', {
                'first_name': '',
                'last_name': '',
                'location': ''
            })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, '')
        self.assertEqual(self.user.last_name, '')
        self.assertEqual(response.url, f'/users/{self.user.username}/')

    def test_follow_change(self):
        '''
        Test change of follow post
        '''
        self.assertEqual(self.user.user_details.follows.count(), 0)
        client = Client()
        client.force_login(self.user)

        response = client.post(f'/users/{self.user.username}/',
                               {'follow': 1})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/users/{self.user.username}/')
        self.assertEqual(self.user.user_details.follows.count(), 1)

    def test_unfollow_change(self):
        '''
        Test change of unfollow post
        '''
        self.user.user_details.follows.add(self.user)
        self.assertEqual(self.user.user_details.follows.count(), 1)
        client = Client()
        client.force_login(self.user)

        response = client.post(f'/users/{self.user.username}/',
                               {'unfollow': 1})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/users/{self.user.username}/')
        self.assertEqual(self.user.user_details.follows.count(), 0)

    def test_user_rating(self):
        '''
        Test the users average rating
        '''
        recipe = Recipes_var.create(
            title='testrecipe',
            slug='testrecipe',
            author=self.user,
            excerpt='about the recipe',
            status=1,
            recipe_image='',
            prep_time=30,
            cook_time=60,
            serves=4,
        )
        StarRating_var.create(user=self.user, recipe=recipe, rating=3)
        client = Client()
        client.force_login(self.user)
        response = client.get(f'/users/{self.user.username}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['average_recipe']['user_recipe_average'],
            3.0)

    def test_following_a_user(self):
        '''
        Test if user is following
        '''
        self.user.user_details.follows.add(self.user)
        client = Client()
        client.force_login(self.user)
        response = client.get(f'/users/{self.user.username}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['is_following'],
            2)


class TestProfilerecipes(TestCase):
    '''
    Test Profile page Recipes Page View
    '''
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='password'
        )
        self.details = UserDetails_var.create(
            user=self.user,
        )
        self.user.user_details = self.details
        self.details.save()
        self.user.save()

        self.user_authenticated = User.objects.create_user(
            username='testuserauthenticated',
            password='password'
        )
        self.details_authenticated = UserDetails_var.create(
            user=self.user_authenticated,
        )
        self.user_authenticated.user_details = self.details_authenticated
        self.details_authenticated.save()
        self.user_authenticated.save()

    def test_get_profile_recipes_page(self):
        '''
        Test Profile Page Recipes status
        '''
        client = Client()
        client.force_login(self.user)
        response = client.get(f'/users/{self.user.username}/myrecipes/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_recipes.html')

    def test_get_profile_recipes_page_other(self):
        '''
        Test Profile Page Recipes status if not your page
        '''
        client = Client()
        client.force_login(self.user)
        response = client.get(
            f'/users/{self.user_authenticated.username}/myrecipes/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_recipes.html')

    def test_get_profile_recipes_page_nouser(self):
        '''
        Test Profile Page Recipes status
        '''
        response = self.client.get('/users/nouser/myrecipes/')
        self.assertEqual(response.status_code, 404)

    def test_post_view(self):
        '''
        Test follow of recipe
        '''
        client = Client()
        client.force_login(self.user_authenticated)
        response = client.post(
            reverse(
                'profile_page_recipes',
                kwargs={'username': self.user.username}),
            {'follow': 'follow'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            f'/users/{self.user.username}/myrecipes/')

    def test_post_view_unfollow(self):
        '''
        Test unfollow of recipe
        '''
        client = Client()
        client.force_login(self.user_authenticated)
        response = client.post(
            reverse(
                    'profile_page_recipes',
                    kwargs={'username': self.user.username}),
            {'unfollow': 'unfollow'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, f'/users/{self.user.username}/myrecipes/')


class TestProfileRecipesAdd(TestCase):
    """
    Test Profile Page Add Recipe View
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='password'
        )
        self.details = UserDetails_var.create(
            user=self.user,
            status=1,
        )
        self.user.user_details = self.details
        self.details.save()
        self.user.save()

        self.user_authenticated = User.objects.create_user(
            username='testuserauthenticated',
            password='password'
        )
        self.details_authenticated = UserDetails_var.create(
            user=self.user_authenticated,
        )
        self.user_authenticated.user_details = self.details_authenticated
        self.details_authenticated.save()
        self.user_authenticated.save()

        self.recipe = Recipes_var.create(
            title='testrecipe',
            slug='testrecipe',
            author=self.user,
            excerpt='about the recipe',
            status=1,
            recipe_image='',
            prep_time=30,
            cook_time=60,
            serves=4
        )

    def test_logged_in_own_page(self):
        '''
        Test logged in and your own page
        '''
        client = Client()
        client.force_login(self.user)
        response = client.get(f'/users/{self.user.username}/myrecipes/new')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_recipes_add.html')

    def test_logged_in_someone_else(self):
        '''
        Test logged in and someone else page
        '''
        client = Client()
        client.force_login(self.user)
        response = client.get(
            f'/users/{self.user_authenticated.username}/myrecipes/new')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/users/testuser/')

    def test_logged_in_someone_else_post(self):
        '''
        Test logged in and someone else page post method
        '''
        client = Client()
        client.force_login(self.user)
        response = client.post(
            f'/users/{self.user_authenticated.username}/myrecipes/new')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/users/testuser/')

    def test_not_logged_in(self):
        '''
        Test not logged in and not own page
        '''
        response = self.client.get(
            f'/users/{self.user_authenticated.username}/myrecipes/new')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/')

    def test_not_logged_in_post(self):
        '''
        Test not logged in and not own page post method
        '''
        response = self.client.post(
            f'/users/{self.user_authenticated.username}/myrecipes/new')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/')

    def generate_test_image(self):
        '''
        A test image to upload
        '''
        image_path = 'media/test_image.jpg'
        new_photo = SimpleUploadedFile(
            name='test_image.jpg',
            content=open(image_path, 'rb').read(),
            content_type='image/jpeg')
        return new_photo

    def test_post_with_valid_data(self):
        '''
        Test recipe with valid data
        '''
        factory = RequestFactory()
        image = self.generate_test_image()
        client = Client()
        client.force_login(self.user)
        form_data = {
            'title': 'Test Recipe',
            'excerpt': 'Test Description',
            'prep_time': 30,
            'cook_time': 60,
            'serves': 3,
            'recipe_image': image,
        }

        request = factory.post(
            reverse('profile_page_recipes_add', args=[self.user.username]),
            data=form_data,
            files=form_data)
        post_data = request.POST.copy()
        post_data.update(form_data)
        request.POST = post_data
        request.FILES.update(form_data)
        request.user = self.user

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = ProfileRecipesAdd.as_view()(
            request,
            username=self.user.username,
            format='multipart/form-data',
            data=form_data,
            files=form_data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(list(messages)[0]), 'Recipe Added')
        self.assertEqual(Recipes_var.count(), 2)

    def test_post_with_invalid_data(self):
        '''
        Test recipe with invalid data
        '''
        client = Client()
        client.force_login(self.user)
        recipe_data = {
            'title': '',
            'excerpt': 'Test Description',
            'prep_time': 30,
            'cook_time': 60,
            'serves': 3,
        }
        data = recipe_data.copy()
        response = client.post(
            reverse(
                'profile_page_recipes_add',
                kwargs={'username': self.user.username}), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Recipes_var.count(), 1)

    def test_status_update_lv1(self):
        '''
        Test update to status 1
        '''
        client = Client()
        client.force_login(self.user)
        for i in range(5):
            recipe_data = {
                'title': f'recipe_{i}',
                'excerpt': 'Test Description',
                'prep_time': 30,
                'cook_time': 60,
                'serves': 3,
                'status': 1,
                'publish': True
            }
            data = recipe_data.copy()
            response = client.post(reverse(
                'profile_page_recipes_add',
                kwargs={'username': self.user.username}), data)
        self.user.user_details.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            self.user.user_recipes.filter(status=1).count(), 6)
        self.assertEqual(
            self.user.user_details.status, 1)

    def test_status_update_lv2(self):
        '''
        Test update to status 2
        '''
        client = Client()
        client.force_login(self.user)
        for i in range(10):
            recipe_data = {
                'title': f'recipe_{i}',
                'excerpt': 'Test Description',
                'prep_time': 30,
                'cook_time': 60,
                'serves': 3,
                'status': 1,
                'publish': True
            }
            data = recipe_data.copy()
            response = client.post(reverse(
                'profile_page_recipes_add',
                kwargs={'username': self.user.username}), data)
        self.user.user_details.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            self.user.user_recipes.filter(status=1).count(), 11)
        self.assertEqual(
            self.user.user_details.status, 2)
        self.assertNotEqual(
            self.user.user_details.status, 1)

    def test_status_update_lv3(self):
        '''
        Test update to status 3
        '''
        client = Client()
        client.force_login(self.user)
        for i in range(20):
            recipe_data = {
                'title': f'recipe_{i}',
                'excerpt': 'Test Description',
                'prep_time': 30,
                'cook_time': 60,
                'serves': 3,
                'status': 1,
                'publish': True
            }
            data = recipe_data.copy()
            response = client.post(reverse(
                'profile_page_recipes_add',
                kwargs={'username': self.user.username}), data)
        self.user.user_details.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            self.user.user_recipes.filter(status=1).count(), 21)
        self.assertEqual(
            self.user.user_details.status, 3)
        self.assertNotEqual(
            self.user.user_details.status, 1)

    def test_status_update_lv4(self):
        '''
        Test update to status 4
        '''
        client = Client()
        client.force_login(self.user)
        for i in range(29):
            recipe_data = {
                'title': f'recipe_{i}',
                'excerpt': 'Test Description',
                'prep_time': 30,
                'cook_time': 60,
                'serves': 3,
                'status': 1,
                'publish': True
            }
            data = recipe_data.copy()
            response = client.post(reverse(
                'profile_page_recipes_add',
                kwargs={'username': self.user.username}), data)
        self.user.user_details.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            self.user.user_recipes.filter(status=1).count(), 30)
        self.assertEqual(
            self.user.user_details.status, 4)
        self.assertNotEqual(
            self.user.user_details.status, 1)

    def test_status_update_lv5(self):
        '''
        Test update to status 5
        '''
        client = Client()
        client.force_login(self.user)
        for i in range(39):
            recipe_data = {
                'title': f'recipe_{i}',
                'excerpt': 'Test Description',
                'prep_time': 30,
                'cook_time': 60,
                'serves': 3,
                'status': 1,
                'publish': True
            }
            data = recipe_data.copy()
            response = client.post(reverse(
                'profile_page_recipes_add',
                kwargs={'username': self.user.username}), data)
        self.user.user_details.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            self.user.user_recipes.filter(status=1).count(), 40)
        self.assertEqual(
            self.user.user_details.status, 5)
        self.assertNotEqual(
            self.user.user_details.status, 1)

    def test_status_update_lv5_plus(self):
        '''
        Test update to status 5 and plus
        '''
        client = Client()
        client.force_login(self.user)
        for i in range(49):
            recipe_data = {
                'title': f'recipe_{i}',
                'excerpt': 'Test Description',
                'prep_time': 30,
                'cook_time': 60,
                'serves': 3,
                'status': 1,
                'publish': True
            }
            data = recipe_data.copy()
            response = client.post(reverse(
                'profile_page_recipes_add',
                kwargs={'username': self.user.username}), data)
        self.user.user_details.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            self.user.user_recipes.filter(status=1).count(), 50)
        self.assertEqual(
            self.user.user_details.status, 5)
        self.assertNotEqual(
            self.user.user_details.status, 6)
        self.assertNotEqual(
            self.user.user_details.status, 1)


class TestProfileRecipesEdit(TestCase):
    """
    Test Profile Page Edit Recipe View
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='password'
        )
        self.details = UserDetails_var.create(
            user=self.user,
        )
        self.user.user_details = self.details
        self.details.save()
        self.user.save()

        self.user_authenticated = User.objects.create_user(
            username='testuserauthenticated',
            password='password'
        )
        self.details_authenticated = UserDetails_var.create(
            user=self.user_authenticated,
        )
        self.user_authenticated.user_details = self.details_authenticated
        self.details_authenticated.save()
        self.user_authenticated.save()

        self.recipe = Recipes_var.create(
            title='testrecipe',
            slug='testrecipe',
            author=self.user,
            excerpt='about the recipe',
            status=1,
            recipe_image='',
            prep_time=30,
            cook_time=60,
            serves=4
        )

        self.recipe_authenticated = Recipes_var.create(
            title='recipe_authenticated',
            slug='recipe_authenticated',
            author=self.user_authenticated,
            excerpt='about the recipe',
            status=1,
            recipe_image='',
            prep_time=30,
            cook_time=60,
            serves=4
        )
        self.unit = Units_var.create(name='unit1')
        self.ingredient = Ingredients_var.create(name='ingredient1')
        self.recipe_item = RecipeItems_var.create(
            recipe=self.recipe,
            ingredients=self.ingredient,
            amount=1,
            unit=self.unit)
        self.method = Methods_var.create(
            recipe=self.recipe,
            method='instruction1',
            order=1)

    def test_logged_in_own_page(self):
        '''
        Test logged in and your own page
        '''
        client = Client()
        client.force_login(self.user)
        response = client.get(
            f'/users/{self.user.username}/myrecipes/edit/{self.recipe.slug}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_recipes_edit.html')

    def test_logged_in_someone_else(self):
        '''
        Test logged in and someone else page
        '''
        username = self.user_authenticated.username
        recipeslug = self.recipe_authenticated.slug
        client = Client()
        client.force_login(self.user)
        response = client.get(
            f'/users/{username}/myrecipes/edit/{recipeslug}')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/users/testuser/')

    def test_not_logged_in(self):
        '''
        Test not logged in and not own page
        '''
        response = self.client.get(
            f'/users/{self.user.username}/myrecipes/edit/{self.recipe.slug}')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/')

    def test_logged_in_someone_else_post(self):
        '''
        Test logged in and someone else page post method
        '''
        username = self.user_authenticated.username
        recipeslug = self.recipe_authenticated.slug
        client = Client()
        client.force_login(self.user)
        response = client.post(
            f'/users/{username}/myrecipes/edit/{recipeslug}')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/users/testuser/')

    def test_not_logged_in_post(self):
        '''
        Test not logged in and not own page post method
        '''
        response = self.client.post(
            f'/users/{self.user.username}/myrecipes/edit/{self.recipe.slug}')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/')

    def generate_test_image(self):
        '''
        A test image to upload
        '''
        image_path = 'media/test_image.jpg'
        new_photo = SimpleUploadedFile(
            name='test_image.jpg',
            content=open(image_path, 'rb').read(),
            content_type='image/jpeg')
        return new_photo

    def test_update_recipe(self):
        '''
        Test update of recipe details
        '''
        factory = RequestFactory()
        image = self.generate_test_image()
        client = Client()
        client.force_login(self.user)
        form_data = {
            'the_recipe_form': 'the_recipe_form',
            'title': 'updated_recipe',
            'author': self.user,
            'excerpt': 'about the recipe',
            'status': 1,
            'recipe_image': image,
            'prep_time': 30,
            'cook_time': 60,
            'serves': 4
        }

        request = factory.post(
            f'/users/{self.user.username}/myrecipes/edit/{self.recipe.slug}',
            data=form_data,
            files=form_data)
        post_data = request.POST.copy()
        post_data.update(form_data)
        request.POST = post_data
        request.FILES.update(form_data)
        request.user = self.user

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = ProfileRecipesEdit.as_view()(
            request,
            username=self.user.username,
            recipe=self.recipe.slug,
            format='multipart/form-data',
            data=form_data,
            files=form_data)

        self.assertEqual(response.status_code, 302)
        self.recipe.refresh_from_db()
        self.assertTrue(
            Recipes_var.filter(title='updated_recipe').exists())
        self.assertEqual(
            response.url,
            f'/users/{self.user.username}/myrecipes/edit/{self.recipe.slug}')
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(list(messages)[0]), 'Recipe Updated')

    def test_update_recipe_invalid(self):
        '''
        Test update of recipe details invalid form
        '''
        content = {
            'the_recipe_form': 'the_recipe_form',
            'title': 'updated_recipe',
            'author': self.user,
            'excerpt': 'about the recipe',
            'status': 1,
            'recipe_image': '',
            'prep_time': '',
            'cook_time': '',
            'serves': ''
        }

        factory = RequestFactory()

        request = factory.post(
            f'/users/{self.user.username}/myrecipes/edit/{self.recipe.slug}',
            recipe=self.recipe.slug,
            data=content)
        post_data = request.POST.copy()
        post_data.update(content)
        request.POST = post_data
        request.user = self.user

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = ProfileRecipesEdit.as_view()(
            request,
            username=self.user.username,
            recipe=self.recipe.slug,
            data=content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(list(messages)[0]), 'Error With Recipe')

    def test_update_recipe_publish(self):
        '''
        Test update of recipe details to publish
        '''
        client = Client()
        client.force_login(self.user)

        content = {

            'the_recipe_form': 'the_recipe_form',
            'title': 'updated_recipe',
            'author': self.user,
            'excerpt': 'about the recipe',
            'status': 1,
            'recipe_image': '',
            'prep_time': 30,
            'cook_time': 60,
            'serves': 4,
            'publish': True,
        }

        response = client.post(
            f'/users/{self.user.username}/myrecipes/edit/{self.recipe.slug}',
            content)
        self.assertEqual(response.status_code, 302)
        self.recipe.refresh_from_db()
        self.assertEqual(
            Recipes_var.filter(status=1).count(), 2)
        self.assertEqual(
            response.url,
            f'/users/{self.user.username}/myrecipes/edit/{self.recipe.slug}')

    def test_update_ingredient(self):
        '''
        Test update of ingredient in recipe
        '''
        client = Client()
        client.force_login(self.user)
        content = {
          'the_ingredient_form': 'the_ingredient_form',
          'ingredients': self.ingredient.id,
          'amount': 2,
          'unit': self.unit.id,
          'recipe': self.recipe,
        }
        response = client.post(
            f'/users/{self.user.username}/myrecipes/edit/{self.recipe.slug}',
            content)
        self.assertEqual(response.status_code, 200)
        self.recipe.refresh_from_db()
        self.assertTrue(RecipeItems_var.filter(amount=2).exists())

    def test_add_ingredient_with_messages(self):
        '''
        Test add of ingredient in recipe
        '''
        ingredient2 = Ingredients_var.create(name='ingredient2')
        content = {
          'the_ingredient_form': 'the_ingredient_form',
          'ingredients': ingredient2.id,
          'amount': 7,
          'unit': self.unit.id,
          'recipe': self.recipe,
        }

        factory = RequestFactory()

        request = factory.post(
            f'/users/{self.user.username}/myrecipes/edit/{self.recipe.slug}',
            recipe=self.recipe.slug,
            data=content)
        post_data = request.POST.copy()
        post_data.update(content)
        request.POST = post_data
        request.user = self.user

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = ProfileRecipesEdit.as_view()(
            request,
            username=self.user.username,
            recipe=self.recipe.slug,
            data=content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(list(messages)[0]), 'Ingredient Added')
        self.recipe.refresh_from_db()
        self.assertTrue(RecipeItems_var.filter(amount=7).exists())

    def test_add_ingredient_with_messages_invalid(self):
        '''
        Test add of ingredient in recipe invalid
        '''
        ingredient2 = Ingredients_var.create(name='ingredient2')
        content = {
          'the_ingredient_form': 'the_ingredient_form',
          'ingredients': ingredient2.id,
          'amount': '',
          'unit': self.unit.id,
          'recipe': self.recipe,
        }

        factory = RequestFactory()

        request = factory.post(
            f'/users/{self.user.username}/myrecipes/edit/{self.recipe.slug}',
            recipe=self.recipe.slug, data=content)
        post_data = request.POST.copy()
        post_data.update(content)
        request.POST = post_data
        request.user = self.user

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = ProfileRecipesEdit.as_view()(
            request, username=self.user.username,
            recipe=self.recipe.slug, data=content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(list(messages)[0]), 'Error With Ingredient')
        self.recipe.refresh_from_db()
        self.assertFalse(
            RecipeItems_var.filter(ingredients=ingredient2.id).exists())

    def test_update_method(self):
        '''
        Test update of method in recipe
        '''
        client = Client()
        client.force_login(self.user)
        content = {
          'the_method_form': 'the_method_form',
          'method': "updated_instruction",
          'order': 2,
          'recipe': self.recipe,
        }
        response = client.post(
            f'/users/{self.user.username}/myrecipes/edit/{self.recipe.slug}',
            content)
        self.assertEqual(response.status_code, 200)
        self.recipe.refresh_from_db()
        self.assertTrue(
            Methods_var.filter(method='updated_instruction').exists())

    def test_update_method_id(self):
        '''
        Test update of method in recipe
        '''
        client = Client()
        client.force_login(self.user)
        content = {
          'the_method_form_id': 1,
          'method': "updated_instruction",
          'order': 2,
          'recipe': self.recipe,
        }
        response = client.post(
            f'/users/{self.user.username}/myrecipes/edit/{self.recipe.slug}',
            content)
        self.assertEqual(response.status_code, 200)
        self.recipe.refresh_from_db()
        self.assertTrue(
            Methods_var.filter(method='updated_instruction').exists())

    def test_delete_recipe(self):
        '''
        Test delete of recipe
        '''
        recipe_1 = Recipes_var.create(
            title='testrecipe1',
            slug='testrecipe1',
            author=self.user,
            excerpt='about the recipe',
            status=1,
            recipe_image='',
            prep_time=30,
            cook_time=60,
            serves=4,
            id=99,
        )
        self.assertEqual(Recipes_var.count(), 3)
        client = Client()
        client.force_login(self.user)
        content = {
          'the_delete_form': 'the_delete_form',
          'id': recipe_1.id
        }
        response = client.post(
            f'/users/{self.user.username}/myrecipes/edit/{self.recipe.slug}',
            content)
        self.assertEqual(response.status_code, 302)
        self.recipe.refresh_from_db()
        self.assertEqual(Recipes_var.count(), 2)
        self.assertEqual(
            response.url, f'/users/{self.user.username}/myrecipes/')

    def test_add_ingredient(self):
        '''
        Test add of ingredients to recipe
        '''
        client = Client()
        client.force_login(self.user)
        content = {
          'the_ingredients_form': 'the_ingredients_form',
          'name': "new_item",
        }
        response = client.post(
            f'/users/{self.user.username}/myrecipes/edit/{self.recipe.slug}',
            content)
        self.assertEqual(response.status_code, 200)
        self.recipe.refresh_from_db()
        self.assertTrue(Ingredients_var.filter(name='new_item').exists())

    def test_delete_recipe_item(self):
        '''
        Test delete of ingredients from recipe
        '''
        response = self.client.delete(
            f'/users/{self.user.username}/myrecipes/edit/{self.recipe.slug}',
            content_type='application/json',
            data=json.dumps({
                'id': self.recipe_item.id,
                'model': 'RecipeItems'
            })
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            RecipeItems_var.filter(id=self.recipe_item.id).exists())
        self.assertDictEqual(
            json.loads(response.content),
            {'message': (self.recipe_item.id), 'last': 0})

    def test_delete_method(self):
        '''
        Test you can delete the method
        '''
        response = self.client.delete(
            f'/users/{self.user.username}/myrecipes/edit/{self.recipe.slug}',
            content_type='application/json',
            data=json.dumps({
                'id': self.method.id,
                'model': 'Methods'
            })
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Methods_var.filter(id=self.method.id).exists())
        self.assertDictEqual(json.loads(response.content),
                             {'message': (self.method.id), 'last': 0})

    def test_delete_last_method(self):
        '''
        Test you can delete the last method
        '''
        Methods_var.create(
            recipe=self.recipe,
            method='instruction2',
            order=2)
        response = self.client.delete(
            f'/users/{self.user.username}/myrecipes/edit/{self.recipe.slug}',
            content_type='application/json',
            data=json.dumps({
                'id': self.method.id,
                'model': 'Methods'
            })
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Methods_var.filter(id=self.method.id).exists())
        self.assertDictEqual(
            json.loads(response.content),
            {'message': (self.method.id), 'last': 1})

    def test_search_term(self):
        '''
        Test when a search term is present
        '''
        client = Client()
        client.force_login(self.user)
        content = {
          'search_term': 'test',
        }
        response = client.get(
            f'/users/{self.user.username}/myrecipes/edit/{self.recipe.slug}',
            content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['go_to_id_id'],
            'ingredients_section')

    def test_page_number(self):
        '''
        Test when on a page not 1
        '''
        client = Client()
        client.force_login(self.user)
        content = {
          'page': 2,
        }
        response = client.get(
            f'/users/{self.user.username}/myrecipes/edit/{self.recipe.slug}',
            content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['go_to_id_id'],
            'ingredients_section')


class TestProfileFollowers(TestCase):
    """
    Test Profile Page Followers View
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='password'
        )
        self.details = UserDetails_var.create(
            user=self.user,
        )
        self.user.user_details = self.details

        self.user_authenticated = User.objects.create_user(
            username='testuserauthenticated',
            password='password'
        )
        self.details_authenticated = UserDetails_var.create(
            user=self.user_authenticated,
        )
        self.user_authenticated.user_details = self.details_authenticated

        self.recipe = Recipes_var.create(
            title='testrecipe',
            slug='testrecipe',
            author=self.user,
            excerpt='about the recipe',
            status=1,
            recipe_image='',
            prep_time=30,
            cook_time=60,
            serves=4
        )

        self.recipe_authenticated = Recipes_var.create(
            title='recipe_authenticated',
            slug='recipe_authenticated',
            author=self.user_authenticated,
            excerpt='about the recipe',
            status=1,
            recipe_image='',
            prep_time=30,
            cook_time=60,
            serves=4
        )

    def test_logged_in_own_page(self):
        '''
        logged in and your own page
        '''
        client = Client()
        client.force_login(self.user)
        response = client.get(f'/users/{self.user.username}/myfollowers/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_followers.html')

    def test_logged_in_someone_else(self):
        '''
        logged in and someone else page
        '''
        client = Client()
        client.force_login(self.user)
        response = client.get(
            f'/users/{self.user_authenticated.username}/myfollowers/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_followers.html')

    def test_not_logged_in(self):
        '''
        not logged in and not own page
        '''
        response = self.client.get(f'/users/{self.user.username}/myfollowers/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_followers.html')

    def test_post_follow(self):
        '''
        Test you can follow
        '''
        client = Client()
        client.force_login(self.user)
        response = client.post(
            f'/users/{self.user_authenticated.username}/myfollowers/',
            {'follow': 'Follow',
             'the_follow_form': self.user_authenticated.username})
        self.assertRedirects(
            response,
            f'/users/{self.user_authenticated.username}/myfollowers/')

    def test_post_unfollow(self):
        '''
        Test you can unfollow
        '''
        client = Client()
        client.force_login(self.user)
        response = client.post(
            f'/users/{self.user_authenticated.username}/myfollowers/',
            {'unfollow': 'Unfollow',
             'the_follow_form': self.user_authenticated.username})
        self.assertRedirects(
            response,
            f'/users/{self.user_authenticated.username}/myfollowers/')

    def test_get_already_following(self):
        '''
        Test if you are already following the user
        '''
        self.user.user_details.follows.add(self.user)
        self.user.user_details.follows.add(self.user_authenticated)
        self.assertEqual(self.user.user_details.follows.count(), 2)
        self.user.user_details.save()
        client = Client()
        client.force_login(self.user)
        response = client.get(f'/users/{self.user.username}/myfollowers/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_followers.html')
        self.assertIn("user_follow_rating", response.context)
        self.assertEqual(
            response.context["user_follow_rating"][0].is_following_data, 2)

    def test_get_not_already_following(self):
        '''
        Test if you are not already following the user
        '''
        self.user.user_details.follows.add(self.user_authenticated)
        self.user.user_details.save()
        self.assertEqual(self.user.user_details.follows.count(), 1)
        client = Client()
        client.force_login(self.user_authenticated)
        response = client.get(f'/users/{self.user.username}/myfollowers/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_followers.html')
        self.assertIn("user_follow_rating", response.context)
        self.assertEqual(
            response.context["user_follow_rating"][0].is_following_data, 1)


class TestProfileFavourites(TestCase):
    """
    Test Profile Page Favourites View
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='password'
        )
        self.details = UserDetails_var.create(
            user=self.user,
        )
        self.user.user_details = self.details
        self.details.save()
        self.user.save()

        self.user_authenticated = User.objects.create_user(
            username='testuserauthenticated',
            password='password'
        )
        self.details_authenticated = UserDetails_var.create(
            user=self.user_authenticated,
        )
        self.user_authenticated.user_details = self.details_authenticated
        self.details_authenticated.save()
        self.user_authenticated.save()

        self.recipe = Recipes_var.create(
            title='testrecipe',
            slug='testrecipe',
            author=self.user,
            excerpt='about the recipe',
            status=1,
            recipe_image='',
            prep_time=30,
            cook_time=60,
            serves=4
        )

        self.recipe_authenticated = Recipes_var.create(
            title='recipe_authenticated',
            slug='recipe_authenticated',
            author=self.user_authenticated,
            excerpt='about the recipe',
            status=1,
            recipe_image='',
            prep_time=30,
            cook_time=60,
            serves=4
        )

    def test_logged_in_own_page(self):
        '''
        Test logged in and your own page
        '''
        client = Client()
        client.force_login(self.user)
        response = client.get(f'/users/{self.user.username}/myfavourites/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_favourites.html')

    def test_logged_in_someone_else(self):
        '''
        Test logged in and someone else page
        '''
        client = Client()
        client.force_login(self.user)
        response = client.get(
            f'/users/{self.user_authenticated.username}/myfavourites/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_favourites.html')

    def test_not_logged_in(self):
        '''
        Test not logged in and not own page
        '''
        response = self.client.get(
            f'/users/{self.user.username}/myfavourites/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_favourites.html')

    def test_post_favourites(self):
        '''
        Test user can favourites
        '''
        client = Client()
        client.force_login(self.user)
        response = client.post(
            f'/users/{self.user.username}/myfavourites/',
            {'follow': 'follow'})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, f'/users/{self.user.username}/myfavourites/')

    def test_post_unfollow_favourites(self):
        '''
        Test user can favourites
        '''
        client = Client()
        client.force_login(self.user)
        response = client.post(
            f'/users/{self.user.username}/myfavourites/',
            {'unfollow': 'unfollow'})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, f'/users/{self.user.username}/myfavourites/')


class TestProfileCurrentUserProfileRedirectView(TestCase):
    """
    Test Profile Page redirect after log in View
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='password'
        )
        self.details = UserDetails_var.create(
            user=self.user,
        )
        self.user.user_details = self.details
        self.details.save()
        self.user.save()

        self.factory = RequestFactory()

    def test_logged_in_own_page(self):
        '''
        Test when logged in
        '''
        client = Client()
        client.force_login(self.user)
        response = client.get('/loggedIn')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['location'], '/loggedIn/')

    def test_not_logged_in(self):
        '''
        Test not logged in
        '''
        response = self.client.get('/loggedIn')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['location'], '/loggedIn/')

    def test_redirect_to_profile_page(self):
        '''
        Test redirect to profile page when logged in
        '''
        request = self.factory.get(reverse('logged_on'))
        request.user = self.user
        response = CurrentUserProfileRedirectView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse(
            'profile_page', args=[self.user.username]))

    def test_redirect_to_login(self):
        '''
        Test redirect to login when not logged on
        '''
        response = self.client.get(reverse('logged_on'))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/accounts/login/?next=/loggedIn/')


class AboutUsTest(TestCase):
    """
    Test About page
    """
    def test_get(self):
        '''
        Test get request on about page
        '''
        url = reverse('aboutus')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about_us.html')

    def test_post_success(self):
        '''
        Test send of contact us form, valid
        '''
        url = reverse('aboutus')
        data = {"status": 1}
        response = self.client.post(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Message"})
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Message Sent')

    def test_post_error(self):
        '''
        Test send of contact us form, invalid
        '''
        url = reverse('aboutus')
        data = {"status": 2}
        response = self.client.post(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Message"})
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Error With Message')


class Custom404Test(TestCase):
    '''
    Test 404
    '''
    def test_custom_404_from_url(self):
        '''
        Test from invalid url
        '''
        url = f'/nothere'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_custom_404(self):
        '''
        Test 404 view
        '''
        factory = RequestFactory()
        response = custom_404(factory)
        self.assertEqual(response.status_code, 404)


class Custom403Test(TestCase):
    '''
    Test 403
    '''
    def test_custom_403(self):
        '''
        Test 403 view
        '''
        factory = RequestFactory()
        response = custom_403(factory)
        self.assertEqual(response.status_code, 403)


class Custom500Test(TestCase):
    '''
    Test 500
    '''
    def test_custom_500(self):
        '''
        Test 500 view
        '''
        factory = RequestFactory()
        response = custom_500(factory)
        self.assertEqual(response.status_code, 500)
