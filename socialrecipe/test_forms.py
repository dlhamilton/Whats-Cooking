"""
Testing of Forms
"""
from unittest.mock import MagicMock
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from .forms import (CommentsForm, RatingForm, RecipeImagesForm, RecipesForm,
                    SearchRecipeForm, FilterRecipeForm, AddToRecipeForm,
                    IngredientsForm, RecipeItemsForm, MethodsForm,
                    UserDetailsForm, FollowForm, UnfollowForm)
from .models import Recipes, Ingredients, Units, User, UserDetails

img_link = 'https://res.cloudinary.com/demo/image/upload/v1581719397/sample.jpg'
Ingredients_var = Ingredients.objects
Units_var = Units.objects
UserDetails_var = UserDetails.objects


class TestRecipeCommentForm(TestCase):
    """
    Testing Comment Form
    """
    def test_comment_is_required(self):
        '''
        Testing Comment cant be empty
        '''
        form = CommentsForm({'body': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('body', form.errors.keys())
        self.assertEqual(form.errors['body'][0], 'This field is required.')

    def test_fields_are_explicit_in_form_metaclass(self):
        '''
        Testing Comment only shows body field
        '''
        form = CommentsForm()
        self.assertEqual(form.Meta.fields, ('body',))

    def test_form_valid_with_valid_input(self):
        '''
        Testing Comment works when valid
        '''
        form = CommentsForm({'body': 'This is a test comment'})
        self.assertTrue(form.is_valid())


class TestRecipeRatingForm(TestCase):
    """
    Testing Recipe Rating Form
    """
    def test_rating_is_required(self):
        '''
        Testing Rating is required
        '''
        form = RatingForm({'rating': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors.keys())
        self.assertEqual(form.errors['rating'][0], 'This field is required.')

    def test_form_renders_correctly(self):
        '''
        Testing Rating is rendering correctly
        '''
        form = RatingForm()
        self.assertIn('type="hidden"', form.as_p())
        self.assertIn('class="d-none"', form.as_p())

    def test_form_valid_with_valid_input(self):
        '''
        Testing Rating is working with valid input
        '''
        form = RatingForm({'rating': 3})
        self.assertTrue(form.is_valid())

    def test_form_invalid_with_invalid_input(self):
        '''
        Testing Rating cannot be letters
        '''
        form = RatingForm({'rating': 'abc'})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {'rating': ['Enter a whole number.']})

    def test_fields_are_explicit_in_form_metaclass(self):
        '''
        Testing Rating only shows rating field
        '''
        form = RatingForm()
        self.assertEqual(form.Meta.fields, ('rating',))


class TestRecipeImageUploadForm(TestCase):
    """
    Testing Recipe Image Upload Form
    """
    def test_image_is_required(self):
        '''
        Test image is required
        '''
        form = RecipeImagesForm({
            'recipe_image': '',
            'headline': 'Test message'
            })
        self.assertFalse(form.is_valid())
        self.assertIn('recipe_image', form.errors.keys())
        self.assertEqual(
            form.errors['recipe_image'][0], 'No file selected!'
            )

    def test_headline_is_required(self):
        '''
        Test headline is required
        '''
        form = RecipeImagesForm({
            'recipe_image': img_link
        })
        self.assertFalse(form.is_valid())
        self.assertIn('headline', form.errors.keys())
        self.assertEqual(
            form.errors['headline'][0], 'This field is required.'
            )

    def test_form_renders_correctly(self):
        '''
        Test headline is only 3 rows high and cloudianry is an image upload
        '''
        form = RecipeImagesForm()
        self.assertIn('type="file"', form.as_p())
        self.assertIn('rows="3"', form.as_p())

    def test_form_valid_with_valid_input(self):
        '''
        Test form is valid with valid inputs
        '''
        image = SimpleUploadedFile(
            "test_image.jpg",
            b"file_content",
            content_type="image/jpeg"
            )
        form_data = {
            'recipe_image': image,
            'headline': 'This is a test headline',
        }
        form = RecipeImagesForm(data=form_data, files=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_with_invalid_headline(self):
        '''
        Test both fields are required
        '''
        form = RecipeImagesForm({
            'recipe_image': '',
            'headline': '',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['headline'][0], 'This field is required.'
            )

    def test_fields_are_explicit_in_form_metaclass(self):
        '''
        Testing Rating only shows the right fields
        '''
        form = RecipeImagesForm()
        self.assertEqual(form.Meta.fields, ('recipe_image', 'headline'))


class RecipesFormTestCase(TestCase):
    """
    Testing Recipes Form
    """
    def test_form_renders_correctly(self):
        '''
        Test form is redering correctly
        '''
        form = RecipesForm()
        self.assertIn('type="checkbox"', form.as_p())
        self.assertIn('label="Publish"', form.as_p())
        self.assertIn('type="file"', form.as_p())

    def test_form_valid_with_valid_input(self):
        '''
        Test form with valid data
        '''
        image = SimpleUploadedFile(
            "test_image.jpg",
            b"file_content",
            content_type="image/jpeg"
            )
        form_data = {
            'title': 'Test Recipe',
            'recipe_image': image,
            'excerpt': 'This is a test excerpt',
            'prep_time': 30,
            'cook_time': 60,
            'serves': 4,
            'publish': True,
        }
        form = RecipesForm(data=form_data, files=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_with_invalid_title(self):
        '''
        Test form with no title
        '''
        form = RecipesForm({
            'title': '',
            'recipe_image': img_link,
            'excerpt': 'This is a test excerpt',
            'prep_time': 30,
            'cook_time': 60,
            'serves': 4,
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['title'][0], 'This field is required.'
            )

    def test_form_invalid_with_invalid_recipe_image(self):
        '''
        Test form works with no image
        '''
        form = RecipesForm({
            'title': 'Test Recipe',
            'recipe_image': '',
            'excerpt': 'This is a test excerpt',
            'prep_time': 30,
            'cook_time': 60,
            'serves': 4,
        })
        self.assertTrue(form.is_valid())

    def test_form_invalid_with_invalid_excerpt(self):
        '''
        Test form with no excerpt
        '''
        form = RecipesForm({
            'title': 'Test Recipe',
            'recipe_image': img_link,
            'excerpt': '',
            'prep_time': 30,
            'cook_time': 60,
            'serves': 4,
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['excerpt'][0], 'This field is required.'
            )

    def test_form_invalid_with_invalid_prep_time(self):
        '''
        Test form with no prep time
        '''
        form = RecipesForm({
            'title': 'Test Recipe',
            'recipe_image': img_link,
            'excerpt': 'This is a test excerpt',
            'prep_time': '',
            'cook_time': 60,
            'serves': 4,
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['prep_time'][0], 'This field is required.'
            )

    def test_form_invalid_with_invalid_cook_time(self):
        '''
        Test form with no cook time
        '''
        form = RecipesForm({
            'title': 'Test Recipe',
            'recipe_image': img_link,
            'excerpt': 'This is a test excerpt',
            'prep_time': 30,
            'cook_time': '',
            'serves': 4,
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['cook_time'][0], 'This field is required.'
            )

    def test_form_invalid_with_invalid_serves(self):
        '''
        Test form with no serves
        '''
        form = RecipesForm({
            'title': 'Test Recipe',
            'recipe_image': img_link,
            'excerpt': 'This is a test excerpt',
            'prep_time': 30,
            'cook_time': 60,
            'serves': '',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['serves'][0], 'This field is required.'
            )

    def test_form_initial_value_of_publish_true(self):
        '''
        Test form with publish True
        '''
        form = RecipesForm({
            'title': 'Test Recipe',
            'recipe_image': img_link,
            'excerpt': 'This is a test excerpt',
            'prep_time': 30,
            'cook_time': 60,
            'serves': 4,
        })
        recipes_mock = MagicMock(spec=Recipes)
        recipes_mock.status = 1
        form = RecipesForm(instance=recipes_mock)
        self.assertEqual(form.fields['publish'].initial, True)

    def test_form_initial_value_of_publish_false(self):
        '''
        Test form with publish False
        '''
        form = RecipesForm({
            'title': 'Test Recipe',
            'recipe_image': img_link,
            'excerpt': 'This is a test excerpt',
            'prep_time': 30,
            'cook_time': 60,
            'serves': 4,
        })
        recipes_mock = MagicMock(spec=Recipes)
        recipes_mock.status = 0
        self.assertEqual(form.fields['publish'].initial, False)

    def test_form_publish_field_not_required(self):
        '''
        Test form with publish blank
        '''
        form = RecipesForm({
            'title': 'Test Recipe',
            'recipe_image': img_link,
            'excerpt': 'This is a test excerpt',
            'prep_time': 30,
            'cook_time': 60,
            'serves': 4,
            'publish': '',
        })
        self.assertTrue(form.is_valid())

    def test_form_prep_time_invalid(self):
        '''
        Test form with prep time with letters
        '''
        form = RecipesForm({
            'title': 'Test Recipe',
            'recipe_image': img_link,
            'excerpt': 'This is a test excerpt',
            'prep_time': 'abc',
            'cook_time': 60,
            'serves': 4,
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {'prep_time': ['Enter a whole number.']})

    def test_form_cook_time_invalid(self):
        '''
        Test form with cook time with letters
        '''
        form = RecipesForm({
            'title': 'Test Recipe',
            'recipe_image': img_link,
            'excerpt': 'This is a test excerpt',
            'prep_time': 30,
            'cook_time': 'abc',
            'serves': 4,
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {'cook_time': ['Enter a whole number.']})

    def test_form_serves_invalid(self):
        '''
        Test form with serves with letters
        '''
        form = RecipesForm({
            'title': 'Test Recipe',
            'recipe_image': img_link,
            'excerpt': 'This is a test excerpt',
            'prep_time': 30,
            'cook_time': 60,
            'serves': 'abc',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {'serves': ['Enter a whole number.']})

    def test_fields_are_explicit_in_form_metaclass(self):
        '''
        Testing Rating only shows the right fields
        '''
        form = RecipesForm()
        self.assertEqual(
            form.Meta.fields,
            ('title',
             'recipe_image',
             'excerpt',
             'prep_time',
             'cook_time',
             'serves',))


class SearchRecipeFormTest(TestCase):
    """
    Testing Search Bar Form
    """
    def test_form_renders_input_element(self):
        '''
        Test form renders parts correctly
        '''
        form = SearchRecipeForm()
        self.assertIn('id="search_query"', form.as_p())
        self.assertIn('placeholder="Search..."', form.as_p())
        self.assertIn('class="form-control"', form.as_p())

    def test_form_input_element_has_max_length(self):
        '''
        Test the form has a max search length
        '''
        form = SearchRecipeForm()
        self.assertEqual(form.fields['search_query'].max_length, 100)

    def test_form_input_element_is_not_required(self):
        '''
        Test the form element is not required
        '''
        form = SearchRecipeForm()
        self.assertFalse(form.fields['search_query'].required)

    def test_form_valid_with_only_search_query(self):
        '''
        Test the search is valid with one element passed
        '''
        form = SearchRecipeForm({'search_query': 'chicken'})
        self.assertTrue(form.is_valid())

    def test_form_valid_with_multiple_search_query(self):
        '''
        Test the search is valid with multiple element passed
        '''
        form = SearchRecipeForm({'search_query': ['chicken', 'carrots']})
        self.assertTrue(form.is_valid())

    def test_form_valid_with_empty_search_query(self):
        '''
        Test form works with empty string
        '''
        form = SearchRecipeForm({'search_query': ''})
        self.assertTrue(form.is_valid())


class FilterRecipeFormTest(TestCase):
    """
    Testing recipe Filter Form
    """
    @classmethod
    def setUpTestData(cls):
        cls.ingredient_1 = Ingredients_var.create(
            name='Tomatoes', approved=True
            )
        cls.ingredient_2 = Ingredients_var.create(
            name='Apple', approved=True
            )
        cls.ingredient_3 = Ingredients_var.create(
            name='Carrots', approved=False
            )

    def test_form_queries_ordered_by_name(self):
        '''
        Test the form is in order
        '''
        form = FilterRecipeForm()
        self.assertEqual(
            form.fields['filter_query'].queryset[0].name, 'Apple'
            )
        self.assertEqual(
            form.fields['filter_query'].queryset[1].name, 'Tomatoes'
            )

    def test_form_valid_with_valid_input(self):
        '''
        Test the form works with valid data
        '''
        form = FilterRecipeForm({
            'filter_query': [self.ingredient_1.pk, self.ingredient_2.pk]
            })
        self.assertTrue(form.is_valid())

    def test_form_invalid_with_empty_input(self):
        '''
        Test the form is invalid with no data
        '''
        form = FilterRecipeForm({'filter_query': []})
        self.assertFalse(form.is_valid())

    def test_form_queries_approved_ingredients_only(self):
        '''
        Test the form shows only approved items
        '''
        form = FilterRecipeForm()
        self.assertEqual(len(form.fields['filter_query'].queryset), 2)
        self.assertEqual(
            form.fields['filter_query'].queryset[1], self.ingredient_1
            )
        self.assertEqual(
            form.fields['filter_query'].queryset[0], self.ingredient_2
            )

    def test_form_renders_checkbox_select_multiple(self):
        '''
        Test the form is showing checkboxes
        '''
        form = FilterRecipeForm()
        self.assertIn('type="checkbox"', form.as_p())


class AddToRecipeFormTestCase(TestCase):
    """
    Test form to search for getting ingridents
    """
    def test_form_with_valid_data(self):
        '''
        Test from works with valid data
        '''
        form_data = {'search_term': 'chicken'}
        form = AddToRecipeForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_search_term_not_required(self):
        '''
        Test from works with valid data
        '''
        form_data = {}
        form = AddToRecipeForm(data=form_data)
        self.assertTrue(form.is_valid())


class IngredientsFormTestCase(TestCase):
    """
    Test Ingredients Form
    """
    def test_form_with_valid_data(self):
        '''
        Testing name works when valid
        '''
        form_data = {'name': 'chicken'}
        form = IngredientsForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_with_missing_name(self):
        '''
        Testing name cant be empty
        '''
        form_data = {}
        form = IngredientsForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {'name': ['This field is required.']})

    def test_save_form(self):
        '''
        Testing form can save
        '''
        form_data = {'name': 'chicken'}
        form = IngredientsForm(data=form_data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(Ingredients_var.count(), 1)
        self.assertEqual(Ingredients_var.first().name, 'chicken')

    def test_fields_are_explicit_in_form_metaclass(self):
        '''
        Testing name only shows body field
        '''
        form = IngredientsForm()
        self.assertEqual(form.Meta.fields, ('name',))


class TestRecipeItemsForm(TestCase):
    """
    Test from to add item to recipe
    """
    @classmethod
    def setUpTestData(cls):
        cls.unit = Units_var.create(
            name='grams'
            )
        cls.ingredient_1 = Ingredients_var.create(
            name='Tomatoes', approved=True
            )

    def test_form_with_valid_data(self):
        '''
        Testing with valid data
        '''
        form_data = {
            'ingredients': self.ingredient_1,
            'amount': 1,
            'unit': self.unit.pk
        }
        form = RecipeItemsForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_with_invalid_ingredients(self):
        '''
        Testing ingredients cant be empty
        '''
        form_data = {
            'ingredients': '',
            'amount': 1,
            'unit': self.unit.pk
        }
        form = RecipeItemsForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('ingredients', form.errors.keys())
        self.assertEqual(
            form.errors['ingredients'][0], 'This field is required.')

    def test_form_with_invalid_amount(self):
        '''
        Testing amount cant be empty
        '''
        form_data = {
            'ingredients': self.ingredient_1,
            'amount': '',
            'unit': self.unit.pk
        }
        form = RecipeItemsForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors.keys())
        self.assertEqual(form.errors['amount'][0], 'This field is required.')

    def test_form_with_invalid_unit(self):
        '''
        Testing unit cant be empty
        '''
        form_data = {
            'ingredients': self.ingredient_1,
            'amount': 1,
            'unit': ''
        }
        form = RecipeItemsForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('unit', form.errors.keys())
        self.assertEqual(form.errors['unit'][0], 'This field is required.')

    def test_fields_are_explicit_in_form_metaclass(self):
        '''
        Testing only shows correct fields
        '''
        form = RecipeItemsForm()
        self.assertEqual(form.Meta.fields, ['ingredients', 'amount', 'unit'])

    def test_unit_field_has_empty_label(self):
        '''
        Testing unit has empty label
        '''
        form = RecipeItemsForm()
        self.assertEqual(form.fields['unit'].empty_label, "Select Unit")

    def test_ingredients_field_has_attrs(self):
        '''
        Testing ingredients has correct id
        '''
        form = RecipeItemsForm()
        self.assertEqual(
            form.fields['ingredients'].widget.attrs.get('id'),
            'ingredient-name'
            )


class MethodsFormTestCase(TestCase):
    """
    Test user adding methods form
    """
    def test_form_with_valid_data(self):
        '''
        Testing with valid data
        '''
        form_data = {
            'method':
            'Boil the water, add salt and pasta, cook for 10 minutes.'
            }
        form = MethodsForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_with_missing_data(self):
        '''
        Testing with missing data
        '''
        form_data = {'method': ''}
        form = MethodsForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('method', form.errors.keys())
        self.assertEqual(form.errors['method'][0], 'This field is required.')

    def test_fields_are_explicit_in_form_metaclass(self):
        '''
        Testing method only shows body field
        '''
        form = MethodsForm()
        self.assertEqual(form.Meta.fields, ('method',))

    def test_form_renders_correctly(self):
        '''
        Testing Rating is rendering correctly
        '''
        form = MethodsForm()
        self.assertIn('class="method-class-design"', form.as_p())
        self.assertIn('rows="4"', form.as_p())


class UserDetailsFormTests(TestCase):
    """
    Test User Details form
    """
    def test_form_with_valid_data(self):
        """
        Test the user details form works
        """
        user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        user_details = UserDetails_var.create(user=user)
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'location': 'London',
        }
        form = UserDetailsForm(data=form_data, instance=user_details)
        self.assertTrue(form.is_valid())
        form.save()
        user = User.objects.get(username='testuser')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')

    def test_form_with_missing_data_last_name(self):
        '''
        Test form with missing last name
        '''
        user = User.objects.create_user(
            username='testuser',
            password='testpassword'
            )
        user_details = UserDetails_var.create(user=user)
        form_data = {
            'first_name': 'John',
            'last_name': '',
            'location': 'London',
        }
        form = UserDetailsForm(data=form_data, instance=user_details)

        self.assertFalse(form.is_valid())
        self.assertIn('last_name', form.errors.keys())
        self.assertEqual(
            form.errors['last_name'][0],
            'This field is required.'
            )

    def test_form_with_missing_data_first_name(self):
        '''
        Test form with missing first name
        '''
        user = User.objects.create_user(
            username='testuser',
            password='testpassword'
            )
        user_details = UserDetails_var.create(user=user)
        form_data = {
            'first_name': '',
            'last_name': 'Doe',
            'location': 'London',
        }
        form = UserDetailsForm(data=form_data, instance=user_details)
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors.keys())
        self.assertEqual(
            form.errors['first_name'][0],
            'This field is required.'
            )

    def test_form_with_missing_data_location(self):
        '''
        Test form with missing location
        '''
        user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        user_details = UserDetails_var.create(user=user)
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'location': '',
        }
        form = UserDetailsForm(data=form_data, instance=user_details)
        self.assertFalse(form.is_valid())
        self.assertIn('location', form.errors.keys())
        self.assertEqual(form.errors['location'][0], 'This field is required.')

    def test_form_with_image(self):
        '''
        Test form with with image upload
        '''
        user = User.objects.create_user(
            username='testuser',
            password='testpassword'
            )
        user_details = UserDetails_var.create(user=user)
        image = SimpleUploadedFile(
            "test_image.jpg",
            b"file_content",
            content_type="image/jpeg"
            )
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'location': 'London',
            'user_image': image,
        }
        form = UserDetailsForm(data=form_data, instance=user_details)
        self.assertTrue(form.is_valid())

    def test_fields_are_explicit_in_form_metaclass(self):
        '''
        Testing user detials only shows the right fields
        '''
        user = User.objects.create_user(
            username='testuser',
            password='testpassword'
            )
        user_details = UserDetails_var.create(user=user)
        form = UserDetailsForm(instance=user_details)
        self.assertEqual(
            form.Meta.fields, (
                'first_name',
                'last_name',
                'location',
                'user_image'
                )
            )


class FollowFormTest(TestCase):
    """
    Test Follow Form
    """
    def test_form_renders_correctly(self):
        '''
        Check form renders correctly
        '''
        form = FollowForm()
        self.assertIn('type="hidden"', form.as_p())
        self.assertIn('class="d-none"', form.as_p())
        self.assertIn('name="follow"', form.as_p())

    def test_form_valid_data(self):
        '''
        Test form with valid data
        '''
        form = FollowForm({'follow': 1})
        self.assertTrue(form.is_valid())

    def test_form_invalid_data(self):
        '''
        Test form with invalid data
        '''
        form = FollowForm({'follow': ''})
        self.assertFalse(form.is_valid())


class UnfollowFormTest(TestCase):
    """
    Test Unfollow Form
    """
    def test_form_renders_correctly(self):
        '''
        Check form renders correctly
        '''
        form = UnfollowForm()
        self.assertIn('type="hidden"', form.as_p())
        self.assertIn('class="d-none"', form.as_p())
        self.assertIn('name="unfollow"', form.as_p())

    def test_form_valid_data(self):
        '''
        Test form with valid data
        '''
        form = UnfollowForm({'unfollow': 1})
        self.assertTrue(form.is_valid())

    def test_form_invalid_data(self):
        '''
        Test form with invalid data
        '''
        form = UnfollowForm({'unfollow': ''})
        self.assertFalse(form.is_valid())
