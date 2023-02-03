"""
Testing of Views
"""
from django.test import TestCase, RequestFactory
from .models import User, Recipes
from django.urls import reverse
from .views import RecipeDetail


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
    def test_get_home_page(self):
        '''
        Test Recipe Page status
        '''
        response = self.client.get('/recipes/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes.html')


class TestRecipeDetail(TestCase):
    """
    Test Single Recipe Page View
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='password'
        )

        self.user_authenticated = User.objects.create_user(
            username='testuserauthenticated',
            password='password'
        )

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

        self.factory = RequestFactory()

    def test_get_recipe_details_with_authenticated_user(self):
        '''
        Test Recipe Page status when user is logged in
        but looking at another user recipe page not hidden
        '''
        request = self.factory.get(reverse('recipe_detail', args=[self.recipe.slug]))
        request.user = self.user_authenticated
        response = self.client.get('/recipes/testrecipe/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipe_detail.html')

    def test_get_recipe_details_with_authenticated_user_hidden(self):
        '''
        Test Recipe Page status when user is logged in
        but looking at another user recipe page hidden
        '''
        request = self.factory.get(reverse('recipe_detail', args=[self.recipe.slug]))
        request.user = self.user_authenticated
        response = self.client.get('/recipes/recipe_hidden/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/')

    def test_get_recipe_details_with_own(self):
        '''
        Test Recipe Page status when user is logged in
        but looking at own recipe page not hidden
        '''
        request = self.factory.get(reverse('recipe_detail', args=[self.recipe.slug]))
        request.user = self.user
        response = self.client.get('/recipes/testrecipe/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipe_detail.html')

    def test_get_recipe_details_with_own_hidden(self):
        '''
        Test Recipe Page status when user is logged in
        but looking at own recipe page hidden
        '''
        request = self.factory.get(reverse('recipe_detail', args=[self.recipe.slug]))
        request.user = self.user
        response = self.client.get('/recipes/testrecipe/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipe_detail.html')

    def test_get_recipe_details_with_not_login_user(self):
        '''
        Test Recipe Page status when user is not logged in
        looking at user recipe page hidden
        '''
        response = self.client.get('/recipes/recipe_hidden/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/')

    def test_get_recipe_details_with__user(self):
        '''
        Test Recipe Page status when user is not logged in
        looking at user recipe page not hidden
        '''
        response = self.client.get('/recipes/testrecipe/')
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

        self.user_authenticated = User.objects.create_user(
            username='testuserauthenticated',
            password='password'
        )

        self.factory = RequestFactory()

    def test_get_home_page(self):
        '''
        Test Profile Page status
        '''
        response = self.client.get('/users/testuser/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_profile_page.html')

    def test_get_home_page_loggedin_own(self):
        '''
        Test Profile Page status logged into own profile page
        '''
        request = self.factory.get(reverse('profile_page', args=[self.user]))
        request.user = self.user

        response = self.client.get('/users/testuser/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_profile_page.html')

    def test_get_home_page_loggedin_else(self):
        '''
        Test Profile Page status when looking at another user logged in
        '''
        request = self.factory.get(reverse('profile_page', args=[self.user]))
        request.user = self.user_authenticated
        response = self.client.get('/users/testuser/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_profile_page.html')
