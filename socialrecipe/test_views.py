"""
Testing of Views
"""
import json
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import (User, Recipes, UserDetails, StarRating, Units,
                     Ingredients, RecipeItems, Methods)
from .views import (RecipeDetail, CurrentUserProfileRedirectView, RecipesList,
                    RecipeImages, Comments)

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

    def test_get_filter(self):
        '''
        Test get for recipe list filter
        '''
        client = Client()
        response = client.get(
            '/recipes/filter/', {'filter_query': ['test1', 'test2']})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes.html')

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
            serves=4
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

    def test_post_view_with_image(self):
        '''
        Test recipe form image upload
        '''
        image = SimpleUploadedFile(
            "file.jpg",
            b"file_content",
            content_type="image/jpeg")
        form_data = {
            'recipe_image': image,
            'headline': 'This is a test headline',
            'the_image_form': 'the_image_form',
        }
        client = Client()
        client.force_login(self.user)
        response = client.post(f'/recipes/{self.recipe.slug}/', form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipe_detail.html')


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

    def test_not_logged_in(self):
        '''
        Test not logged in and not own page
        '''
        response = self.client.get(
            f'/users/{self.user_authenticated.username}/myrecipes/new')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/')

    def test_post_with_valid_data(self):
        '''
        Test recipe with valid data
        '''
        client = Client()
        client.force_login(self.user)
        recipe_data = {
            'title': 'Test Recipe',
            'excerpt': 'Test Description',
            'prep_time': 30,
            'cook_time': 60,
            'serves': 3,
        }
        data = recipe_data.copy()
        response = client.post(reverse(
            'profile_page_recipes_add',
            kwargs={'username': self.user.username}), data)
        self.assertEqual(response.status_code, 302)
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

    def test_update_recipe(self):
        '''
        Test update of recipe details
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
            'serves': 4
        }

        response = client.post(
            f'/users/{self.user.username}/myrecipes/edit/{self.recipe.slug}',
            content)
        self.assertEqual(response.status_code, 302)
        self.recipe.refresh_from_db()
        self.assertTrue(
            Recipes_var.filter(title='updated_recipe').exists())
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
            {'message': (self.method.id), 'last': 0})


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
            {'follow': 'Follow'})
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
            {'unfollow': 'Unfollow'})
        self.assertRedirects(
            response,
            f'/users/{self.user_authenticated.username}/myfollowers/')


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

    def test_post_follow(self):
        '''
        Test user can follow
        '''
        client = Client()
        client.force_login(self.user)
        response = client.post(
            f'/users/{self.user.username}/myfollowers/',
            {'follow': 'follow'})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, f'/users/{self.user.username}/myfollowers/')

    def test_post_unfollow(self):
        '''
        Test user can unfollow
        '''
        client = Client()
        client.force_login(self.user)
        response = client.post(
            f'/users/{self.user.username}/myfollowers/',
            {'unfollow': 'unfollow'})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, f'/users/{self.user.username}/myfollowers/')


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
