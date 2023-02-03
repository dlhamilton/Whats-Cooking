"""
Testing of Views
"""
from django.test import TestCase, Client, RequestFactory
from .models import User, Recipes, UserDetails, StarRating
from django.urls import reverse
from .views import RecipeDetail, CurrentUserProfileRedirectView, RecipesList, RecipeImages, Comments
import json
from django.core.files.uploadedfile import SimpleUploadedFile


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

        self.details = UserDetails.objects.create(
            user=self.user,
        )
        self.user.user_details = self.details

        self.recipe = Recipes.objects.create(
            title='Test Recipe',
            slug='test_recipe',
            author=self.user,
            status=1,
            upload_date='2022-12-01'
        )
        self.rating = StarRating.objects.create(
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
        response = client.get('/recipes/filter/', {'filter_query': ['test1', 'test2']})
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
        recipes_list = Recipes.objects.filter(status=1).order_by('-upload_date')
        sorted_recipes = view.sort_functions(recipes_list, {'sort_type': 'name'})
        self.assertEqual(sorted_recipes[0], self.recipe)

        # Test sort by rating
        recipes_list = Recipes.objects.filter(status=1).order_by('-upload_date')
        sorted_recipes = view.sort_functions(recipes_list, {'sort_type': 'rating'})
        self.assertEqual(sorted_recipes[0], self.recipe)

        # Test sort by favourite
        recipes_list = Recipes.objects.filter(status=1).order_by('-upload_date')
        sorted_recipes = view.sort_functions(recipes_list, {'sort_type': 'favourite'})
        self.assertEqual(sorted_recipes[0], self.recipe)

        # Test sort by date
        recipes_list = Recipes.objects.filter(status=1).order_by('-upload_date')
        sorted_recipes = view.sort_functions(recipes_list, {'sort_type': 'date'})
        self.assertEqual(sorted_recipes[0], self.recipe)

        # Test sort by time
        recipes_list = Recipes.objects.filter(status=1).order_by('-upload_date')
        sorted_recipes = view.sort_functions(recipes_list, {'sort_type': 'time'})
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
        self.details = UserDetails.objects.create(
            user=self.user,
        )
        self.user.user_details = self.details
        self.details.save()
        self.user.save()

        self.user_authenticated = User.objects.create_user(
            username='testuserauthenticated',
            password='password'
        )
        self.details_authenticated = UserDetails.objects.create(
            user=self.user_authenticated,
        )
        self.user_authenticated.user_details = self.details_authenticated
        self.details_authenticated.save()
        self.user_authenticated.save()

        self.recipe = Recipes.objects.create(
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

        self.recipe_hidden = Recipes.objects.create(
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

        self.recipe_authenticated = Recipes.objects.create(
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

        
        self.image1 = RecipeImages.objects.create(
            recipe_image="path/to/image1.jpg",
            recipe=self.recipe,
            user=self.user,
        )
        self.image2 = RecipeImages.objects.create(
            recipe_image="path/to/image2.jpg",
            recipe=self.recipe,
            user=self.user,
        )
        self.comment1 = Comments.objects.create(
            body="Comment 1",
            recipe=self.recipe,
            user=self.user,
        )
        self.comment2 = Comments.objects.create(
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
        request = self.factory.get(reverse('recipe_detail', args=[self.recipe.slug]))
        request.user = self.user
        response = RecipeDetail.as_view()(request, slug=self.recipe.slug)
        self.assertContains(response, self.recipe.title)
    
    def test_view_redirects_if_not_author_or_published(self):
        self.recipe.status = 0
        self.recipe.save()
        response = self.client.get(f'/recipes/{self.recipe.slug}/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/')

    def test_view_shows_rated_recipe(self):
        StarRating.objects.create(user=self.user, recipe=self.recipe, rating=3)
        request = self.factory.get(reverse('recipe_detail', args=[self.recipe.slug]))
        request.user = self.user
        response = RecipeDetail.as_view()(request, slug=self.recipe.slug)

    def test_delete_comment(self):
        # send a delete request for the first comment
        response = self.client.delete(
            f'/recipes/{self.recipe.slug}/', 
            content_type='application/json',
            data=json.dumps({
                "model": "comment",
                "id": self.comment1.id
            })
        )
        # check if the comment was deleted
        self.assertEqual(
            response.status_code, 
            200
        )
        self.assertFalse(
            Comments.objects.filter(id=self.comment1.id).exists()
        )
        self.assertTrue(
            Comments.objects.filter(id=self.comment2.id).exists()
        )

    def test_delete_image(self):
        # send a delete request for the first image
        response = self.client.delete(
            f'/recipes/{self.recipe.slug}/',
            content_type='application/json',
            data=json.dumps({
                "model": "recipe_images",
                "id": self.image1.id
            })
        )
        # check if the image was deleted
        self.assertEqual(
            response.status_code, 
            200
        )
        self.assertFalse(
            RecipeImages.objects.filter(id=self.image1.id).exists()
        )
        self.assertTrue(
            RecipeImages.objects.filter(id=self.image2.id).exists()
        )

    def test_delete_nonexistent_record(self):
        # send a delete request for an id that doesn't exist
        response = self.client.delete(
            f'/recipes/{self.recipe.slug}/',
            content_type='application/json',
            data=json.dumps({
                "model": "recipe_images",
                "id": 999
            })
        )
        # check if the response returns a 404 status code
        self.assertEqual(
            response.status_code, 
            404
        )

    def test_post_view_with_comment(self):
        client = Client()
        client.force_login(self.user)
        content = {'body': 'Test comment','the_comment_form': 'the_comment_form'}
        response = client.post(f'/recipes/{self.recipe.slug}/',content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.recipe.comments.count(), 3)
        self.assertTemplateUsed(response, 'recipe_detail.html')

    def test_post_view_with_rating(self):
        client = Client()
        client.force_login(self.user)
        content = {'the_rating_form': 'the_rating_form', 'rating': 4}
        response = client.post(f'/recipes/{self.recipe.slug}/',content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(StarRating.objects.count(), 1)

    def test_post_view_with_image(self):
        image = SimpleUploadedFile("file.jpg", b"file_content", content_type="image/jpeg")

        form_data = {
            'recipe_image': image,
            'headline': 'This is a test headline',
            'the_image_form': 'the_image_form',
        }
        client = Client()
        client.force_login(self.user)
        response = client.post(f'/recipes/{self.recipe.slug}/',form_data)
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
        self.details = UserDetails.objects.create(
            user=self.user,
        )
        self.user.user_details = self.details
        self.details.save()
        self.user.save()

        self.user_authenticated = User.objects.create_user(
            username='testuserauthenticated',
            password='password'
        )
        self.details_authenticated = UserDetails.objects.create(
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


class TestProfilerecipes(TestCase):
    '''
    Test Profile page Recipes Page View
    '''
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='password'
        )
        self.details = UserDetails.objects.create(
            user=self.user,
        )
        self.user.user_details = self.details
        self.details.save()
        self.user.save()

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


class TestProfileRecipesAdd(TestCase):
    """
    Test Profile Page Add Recipe View
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='password'
        )
        self.details = UserDetails.objects.create(
            user=self.user,
        )
        self.user.user_details = self.details
        self.details.save()
        self.user.save()

        self.user_authenticated = User.objects.create_user(
            username='testuserauthenticated',
            password='password'
        )
        self.details_authenticated = UserDetails.objects.create(
            user=self.user_authenticated,
        )
        self.user_authenticated.user_details = self.details_authenticated
        self.details_authenticated.save()
        self.user_authenticated.save()

        self.recipe = Recipes.objects.create(
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

        self.recipe_hidden = Recipes.objects.create(
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

    def test_logged_in_own_page(self):
        '''
        logged in and your own page
        '''
        client = Client()
        client.force_login(self.user)
        response = client.get(f'/users/{self.user.username}/myrecipes/new')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_recipes_add.html')

    def test_logged_in_someone_else(self):
        '''
        logged in and someone else page
        '''
        client = Client()
        client.force_login(self.user)
        response = client.get(f'/users/{self.user_authenticated.username}/myrecipes/new')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/users/testuser/')

    def test_not_logged_in(self):
        '''
        not logged in and not own page
        '''
        response = self.client.get(f'/users/{self.user_authenticated.username}/myrecipes/new')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/')


class TestProfileRecipesEdit(TestCase):
    """
    Test Profile Page Edit Recipe View
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='password'
        )
        self.details = UserDetails.objects.create(
            user=self.user,
        )
        self.user.user_details = self.details
        self.details.save()
        self.user.save()

        self.user_authenticated = User.objects.create_user(
            username='testuserauthenticated',
            password='password'
        )
        self.details_authenticated = UserDetails.objects.create(
            user=self.user_authenticated,
        )
        self.user_authenticated.user_details = self.details_authenticated
        self.details_authenticated.save()
        self.user_authenticated.save()

        self.recipe = Recipes.objects.create(
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

        self.recipe_authenticated = Recipes.objects.create(
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
        response = client.get(f'/users/{self.user.username}/myrecipes/edit/{self.recipe.slug}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_recipes_edit.html')

    def test_logged_in_someone_else(self):
        '''
        logged in and someone else page
        '''
        client = Client()
        client.force_login(self.user)
        response = client.get(f'/users/{self.user_authenticated.username}/myrecipes/edit/{self.recipe_authenticated.slug}')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/users/testuser/')

    def test_not_logged_in(self):
        '''
        not logged in and not own page
        '''
        response = self.client.get(f'/users/{self.user.username}/myrecipes/edit/{self.recipe.slug}')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/')


class TestProfileFollowers(TestCase):
    """
    Test Profile Page Followers View
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='password'
        )
        self.details = UserDetails.objects.create(
            user=self.user,
        )
        self.user.user_details = self.details
        self.details.save()
        self.user.save()

        self.user_authenticated = User.objects.create_user(
            username='testuserauthenticated',
            password='password'
        )
        self.details_authenticated = UserDetails.objects.create(
            user=self.user_authenticated,
        )
        self.user_authenticated.user_details = self.details_authenticated
        self.details_authenticated.save()
        self.user_authenticated.save()

        self.recipe = Recipes.objects.create(
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

        self.recipe_authenticated = Recipes.objects.create(
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
        response = client.get(f'/users/{self.user_authenticated.username}/myfollowers/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_followers.html')

    def test_not_logged_in(self):
        '''
        not logged in and not own page
        '''
        response = self.client.get(f'/users/{self.user.username}/myfollowers/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_followers.html')


class TestProfileFavourites(TestCase):
    """
    Test Profile Page Favourites View
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='password'
        )
        self.details = UserDetails.objects.create(
            user=self.user,
        )
        self.user.user_details = self.details
        self.details.save()
        self.user.save()

        self.user_authenticated = User.objects.create_user(
            username='testuserauthenticated',
            password='password'
        )
        self.details_authenticated = UserDetails.objects.create(
            user=self.user_authenticated,
        )
        self.user_authenticated.user_details = self.details_authenticated
        self.details_authenticated.save()
        self.user_authenticated.save()

        self.recipe = Recipes.objects.create(
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

        self.recipe_authenticated = Recipes.objects.create(
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
        response = client.get(f'/users/{self.user.username}/myfavourites/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_favourites.html')

    def test_logged_in_someone_else(self):
        '''
        logged in and someone else page
        '''
        client = Client()
        client.force_login(self.user)
        response = client.get(f'/users/{self.user_authenticated.username}/myfavourites/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_favourites.html')

    def test_not_logged_in(self):
        '''
        not logged in and not own page
        '''
        response = self.client.get(f'/users/{self.user.username}/myfavourites/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_favourites.html')


class TestProfileCurrentUserProfileRedirectView(TestCase):
    """
    Test Profile Page redirect after log in View
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='password'
        )
        self.details = UserDetails.objects.create(
            user=self.user,
        )
        self.user.user_details = self.details
        self.details.save()
        self.user.save()

        self.factory = RequestFactory()

    def test_logged_in_own_page(self):
        '''
        logged in
        '''
        client = Client()
        client.force_login(self.user)
        response = client.get('/loggedIn')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['location'], '/loggedIn/')

    def test_not_logged_in(self):
        '''
        not logged in
        '''

        response = self.client.get('/loggedIn')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['location'], '/loggedIn/')

    def test_redirect_to_profile_page(self):
        request = self.factory.get(reverse('logged_on'))
        request.user = self.user
        response = CurrentUserProfileRedirectView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('profile_page', args=[self.user.username]))

