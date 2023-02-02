from unittest.mock import MagicMock
from django.test import TestCase
from .forms import CommentsForm, RatingForm, RecipeImagesForm, RecipesForm, SearchRecipeForm, FilterRecipeForm
from .models import Recipes, Ingredients


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
            form.errors['recipe_image'][0], 'This field is required.'
            )

    def test_headline_is_required(self):
        '''
        Test headline is required
        '''
        form = RecipeImagesForm({
            'recipe_image': 'https://res.cloudinary.com/demo/image/upload/v1581719397/sample.jpg',
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
        form = RecipeImagesForm({
            'recipe_image': 'https://res.cloudinary.com/demo/image/upload/v1581719397/sample.jpg',
            'headline': 'This is a test headline',
        })
        self.assertTrue(form.is_valid())

    def test_form_invalid_with_invalid_input(self):
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
        self.assertEqual(
            form.errors['recipe_image'][0],
            'This field is required.'
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
        form = RecipesForm({
            'title': 'Test Recipe',
            'recipe_image': 'https://res.cloudinary.com/demo/image/upload/v1581719397/sample.jpg',
            'excerpt': 'This is a test excerpt',
            'prep_time': 30,
            'cook_time': 60,
            'serves': 4,
            'publish': True,
        })
        self.assertTrue(form.is_valid())

    def test_form_invalid_with_invalid_title(self):
        '''
        Test form with no title
        '''
        form = RecipesForm({
            'title': '',
            'recipe_image': 'https://res.cloudinary.com/demo/image/upload/v1581719397/sample.jpg',
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
        Test form with no image
        '''
        form = RecipesForm({
            'title': 'Test Recipe',
            'recipe_image': '',
            'excerpt': 'This is a test excerpt',
            'prep_time': 30,
            'cook_time': 60,
            'serves': 4,
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['recipe_image'][0], 'This field is required.'
            )

    def test_form_invalid_with_invalid_excerpt(self):
        '''
        Test form with no excerpt
        '''
        form = RecipesForm({
            'title': 'Test Recipe',
            'recipe_image': 'https://res.cloudinary.com/demo/image/upload/v1581719397/sample.jpg',
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
            'recipe_image': 'https://res.cloudinary.com/demo/image/upload/v1581719397/sample.jpg',
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
            'recipe_image': 'https://res.cloudinary.com/demo/image/upload/v1581719397/sample.jpg',
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
            'recipe_image': 'https://res.cloudinary.com/demo/image/upload/v1581719397/sample.jpg',
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
            'recipe_image': 'https://res.cloudinary.com/demo/image/upload/v1581719397/sample.jpg',
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
            'recipe_image': 'https://res.cloudinary.com/demo/image/upload/v1581719397/sample.jpg',
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
            'recipe_image': 'https://res.cloudinary.com/demo/image/upload/v1581719397/sample.jpg',
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
            'recipe_image': 'https://res.cloudinary.com/demo/image/upload/v1581719397/sample.jpg',
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
            'recipe_image': 'https://res.cloudinary.com/demo/image/upload/v1581719397/sample.jpg',
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
            'recipe_image': 'https://res.cloudinary.com/demo/image/upload/v1581719397/sample.jpg',
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
    def test_form_renders_input_element(self):
        form = SearchRecipeForm()
        self.assertIn('id="search_query"', form.as_p())
        self.assertIn('placeholder="Search..."', form.as_p())
        self.assertIn('class="form-control"', form.as_p())

    def test_form_input_element_has_max_length(self):
        form = SearchRecipeForm()
        self.assertEqual(form.fields['search_query'].max_length, 100)

    def test_form_input_element_is_not_required(self):
        form = SearchRecipeForm()
        self.assertFalse(form.fields['search_query'].required)

    def test_form_valid_with_only_search_query(self):
        form = SearchRecipeForm({'search_query': 'chicken'})
        self.assertTrue(form.is_valid())

    def test_form_valid_with_empty_search_query(self):
        form = SearchRecipeForm({'search_query': ''})
        self.assertTrue(form.is_valid())


class FilterRecipeFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.ingredient_1 = Ingredients.objects.create(
            name='Tomatoes', approved=True
            )
        cls.ingredient_2 = Ingredients.objects.create(
            name='Apple', approved=True
            )
        cls.ingredient_3 = Ingredients.objects.create(
            name='Carrots', approved=False
            )

    def test_form_queries_ordered_by_name(self):
        form = FilterRecipeForm()
        self.assertEqual(
            form.fields['filter_query'].queryset[0].name, 'Apple'
            )
        self.assertEqual(
            form.fields['filter_query'].queryset[1].name, 'Tomatoes'
            )

    def test_form_valid_with_valid_input(self):
        form = FilterRecipeForm({
            'filter_query': [self.ingredient_1.pk, self.ingredient_2.pk]
            })
        self.assertTrue(form.is_valid())

    def test_form_invalid_with_empty_input(self):
        form = FilterRecipeForm({'filter_query': []})
        self.assertFalse(form.is_valid())

    def test_form_queries_approved_ingredients_only(self):
        form = FilterRecipeForm()
        self.assertEqual(len(form.fields['filter_query'].queryset), 2)
        self.assertEqual(
            form.fields['filter_query'].queryset[1], self.ingredient_1
            )
        self.assertEqual(
            form.fields['filter_query'].queryset[0], self.ingredient_2
            )

    def test_form_renders_checkbox_select_multiple(self):
        form = FilterRecipeForm()
        self.assertIn('type="checkbox"', form.as_p())
