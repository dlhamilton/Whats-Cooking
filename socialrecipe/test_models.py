from django.test import TestCase
from allauth.account.signals import user_signed_up
from .models import (User, UserDetails, Recipes, Methods, Comments,
                     StarRating, Ingredients)

UserDetails_var = UserDetails.objects
Recipes_var = Recipes.objects
Comments_var = Comments.objects
Methods_var = Methods.objects
StarRating_var = StarRating.objects
Ingredients_var = Ingredients.objects


class TestUserDetailsModels(TestCase):
    '''
    Test Model UserDetails
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

    def test_status_default(self):
        '''
        Test status on default
        '''
        self.assertEqual(self.user.user_details.status, 1)

    def test_user_image_default(self):
        '''
        Test user_image on default
        '''
        self.assertEqual(
            self.user.user_details.user_image,
            'v1670885027/placeholder.jpg')

    def test_follow_count(self):
        '''
        Test follower count function
        '''
        user_a = User.objects.create_user(
            username='testuser_a',
            password='password'
        )
        self.assertEqual(self.user.user_details.number_of_follows(), 0)
        self.user.user_details.follows.set({user_a})
        self.assertEqual(self.user.user_details.number_of_follows(), 1)

    def test_get_all_follows(self):
        '''
        Test get followers function
        '''
        user_a = User.objects.create_user(
            username='testuser_a',
            password='password'
        )
        self.user.user_details.follows.set({user_a})
        self.assertTrue(
            self.user.user_details.get_followers().filter(
                username=user_a.username).exists())

    def test_get_amount_of_recipes(self):
        '''
        Test recipes count function
        '''
        for i in range(5):
            Recipes_var.create(
                author=self.user,
                title=f'recipe_{i}',
                slug=f'recipe_{i}')
        self.assertEqual(
            self.user.user_details.get_amount_of_recipes(), 5 % 10)

    def test_get_amount_to_next(self):
        '''
        Test recipe count to next status function
        '''
        for i in range(5):
            Recipes_var.create(
                author=self.user,
                title=f'recipe_{i}',
                slug=f'recipe_{i}')
        self.assertEqual(
            self.user.user_details.get_amount_to_next(), 10 - 5 % 10)


class TestRecipesModels(TestCase):
    '''
    Test Model Recipes
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
        self.recipe = Recipes_var.create(
            title='testrecipe',
            slug='testrecipe',
            author=self.user,
            excerpt='about the recipe',
            prep_time=30,
            cook_time=60,
        )

    def test_recipe_image_default(self):
        '''
        Test recipe_image on default
        '''
        self.assertEqual(
            self.recipe.recipe_image,
            'v1675027391/placeholder-recipe.png')

    def test_status_default(self):
        '''
        Test status on default
        '''
        self.assertEqual(self.recipe.status, 0)

    def test_serves_default(self):
        '''
        Test serves on default
        '''
        self.assertEqual(self.recipe.serves, 1)

    def test_number_of_favourites(self):
        '''
        Test follower count function
        '''
        user_a = User.objects.create_user(
            username='testuser_a',
            password='password'
        )
        self.assertEqual(self.recipe.number_of_favourites(), 0)
        self.recipe.favourites.set({user_a})
        self.assertEqual(self.recipe.number_of_favourites(), 1)

    def test_total_time_default(self):
        '''
        Test serves on default
        '''
        self.assertEqual(self.recipe.total_time(), 90)


class TestCommentsModels(TestCase):
    '''
    Test Model Comments
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
        self.recipe = Recipes_var.create(
            title='testrecipe',
            slug='testrecipe',
            author=self.user,
            excerpt='about the recipe',
            prep_time=30,
            cook_time=60,
        )
        self.comment = Comments_var.create(
            recipe=self.recipe,
            user=self.user,
            body='test comment',
        )

    def test_status_default(self):
        '''
        Test status on default
        '''
        self.assertEqual(self.comment.status, 1)


class TestMethodsModels(TestCase):
    '''
    Test Model Methods
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
        self.recipe = Recipes_var.create(
            title='testrecipe',
            slug='testrecipe',
            author=self.user,
            excerpt='about the recipe',
            prep_time=30,
            cook_time=60,
        )
        self.method = Methods_var.create(
            recipe=self.recipe,
            order=1,
            method='test method',
        )

    def test_follow_count(self):
        self.assertEqual(self.method.number_of_methods(self.method.pk), 1)


class TestStarRatingModels(TestCase):
    '''
    Test Model StarRating
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
        self.recipe = Recipes_var.create(
            title='testrecipe',
            slug='testrecipe',
            author=self.user,
            excerpt='about the recipe',
            prep_time=30,
            cook_time=60,
        )
        self.starrating = StarRating_var.create(
            recipe=self.recipe,
            user=self.user,
            rating=4,
        )
        self.starrating1 = StarRating_var.create(
            recipe=self.recipe,
            user=self.user,
            rating=4,
        )
        self.starrating2 = StarRating_var.create(
            recipe=self.recipe,
            user=self.user,
            rating=2,
        )

    def test_get_average(self):
        self.assertEqual(
            self.starrating.get_average(self.recipe.pk), (4+4+2)/3)


class TestIngredientsModels(TestCase):
    '''
    Test Model Ingredients
    '''
    def setUp(self):
        self.ingredient = Ingredients_var.create(
            name='testuser',
        )

    def test_approved_default(self):
        '''
        Test approved on default
        '''
        self.assertFalse(self.ingredient.approved)


class TestCreateUserDetails(TestCase):
    def test_after_user_signed_up(self):
        '''
        Test after_user_signed_up user details creation
        '''
        user = User.objects.create_user(
            username='testuser', password='password')
        self.assertFalse(UserDetails_var.filter(user=user).exists())
        user_signed_up.send(sender=User, request=None, user=user)
        self.assertTrue(UserDetails_var.filter(user=user).exists())
