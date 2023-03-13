"""
Socialrecipe forms
"""
from django import forms
from cloudinary.models import CloudinaryField
from allauth.account.forms import SignupForm
from .models import (Comments, Ingredients, Recipes, RecipeItems, Units,
                     Methods, UserDetails, StarRating, RecipeImages)

Ingredients_obj = Ingredients.objects
Units_obj = Units.objects


class CommentsForm(forms.ModelForm):
    '''
    Form to add new comments to recipe
    '''
    class Meta:
        '''
        Meta data
        '''
        model = Comments
        fields = ('body',)


class RatingForm(forms.ModelForm):
    '''
    Form to add new rating to recipe
    '''
    class Meta:
        '''
        Meta data
        '''
        model = StarRating
        fields = ('rating',)
        widgets = {
                    'rating': forms.HiddenInput(attrs={'class': 'd-none'}),
        }


class RecipeImagesForm(forms.ModelForm):
    '''
    Form to add new Image to recipe
    '''
    recipe_image = CloudinaryField('image')
    headline = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))

    class Meta:
        '''
        Meta data
        '''
        model = RecipeImages
        fields = ('recipe_image', 'headline',)

    def clean(self):
        '''
        clean the form data
        '''
        cleaned_data = super().clean()
        recipe_image = cleaned_data.get('recipe_image')
        if not recipe_image:
            self.add_error('recipe_image', 'This field is required.')


class RecipesForm(forms.ModelForm):
    '''
    Form to add new recipe
    '''
    publish = forms.BooleanField(
        initial=False,
        required=False,
        widget=forms.CheckboxInput(attrs={'label': 'Publish'}))
    recipe_image = CloudinaryField('image')

    class Meta:
        '''
        Meta data
        '''
        model = Recipes
        fields = ('title',
                  'recipe_image',
                  'excerpt',
                  'prep_time',
                  'cook_time',
                  'serves',)
        widgets = {
            'excerpt': forms.Textarea(attrs={'required': True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.status == 1:
            self.fields['publish'].initial = True


class SearchRecipeForm(forms.Form):
    '''
    Form to search for a recipe
    '''
    search_query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={'id': 'search_query',
                   'placeholder': 'Search...', 'class': 'form-control'}))


class FilterRecipeForm(forms.Form):
    '''
    Form to filter ingredients for a recipe
    '''
    filter_query = forms.ModelMultipleChoiceField(
        queryset=Ingredients_obj.filter(approved=True).order_by('name'),
        widget=forms.CheckboxSelectMultiple
    )


class AddToRecipeForm(forms.Form):
    '''
    Form to search for an Ingredient for a recipe
    '''
    search_term = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'aria-label': 'Search'}))


class IngredientsForm(forms.ModelForm):
    '''
    Form to add new Ingredient
    '''
    class Meta:
        '''
        Meta data
        '''
        model = Ingredients
        fields = ('name',)


class RecipeItemsForm(forms.ModelForm):
    '''
    Form to add new Ingredient to a recipe
    '''
    class Meta:
        '''
        Meta data
        '''
        model = RecipeItems
        fields = ['ingredients', 'amount', 'unit']
        widgets = {
            'ingredients': forms.TextInput(attrs={'id': 'recipient-name'}),
        }

    unit = forms.ModelChoiceField(queryset=Units_obj.all())

    def __init__(self, *args, **kwargs):
        super(RecipeItemsForm, self).__init__(*args, **kwargs)
        self.fields['unit'].empty_label = "Select Unit"
        self.fields['ingredients'].widget.attrs.update(
            {'id': 'ingredient-name'})


class MethodsForm(forms.ModelForm):
    '''
    Form to add new method to a recipe
    '''
    class Meta:
        '''
        Meta data
        '''
        model = Methods
        fields = ('method',)
        widgets = {
            'method': forms.Textarea(
                attrs={'rows': 4, 'class': 'method-class-design'})
        }


class UserDetailsForm(forms.ModelForm):
    '''
    Form to complete the user account details
    '''
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    location = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    user_image = CloudinaryField('image')

    class Meta:
        '''
        Meta data
        '''
        model = UserDetails
        fields = ('first_name', 'last_name', 'location', 'user_image')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].initial = self.instance.user.first_name
        self.fields['last_name'].initial = self.instance.user.last_name

    def save(self, commit=True):
        user = self.instance.user
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.save()
        return super().save(commit)


class FollowForm(forms.Form):
    '''
    Form to follow a user profile
    '''
    follow = forms.IntegerField(
        widget=forms.HiddenInput(attrs={'class': 'd-none'}), required=False)


class UnfollowForm(forms.Form):
    '''
    Form to unfollow a user profile
    '''
    unfollow = forms.IntegerField(
        widget=forms.HiddenInput(attrs={'class': 'd-none'}), required=False)


class MyCustomSignupForm(SignupForm):
    '''
    Form to sign up as a new user
    '''
    def clean_username(self):
        '''
        username cleaning to get rid of certain characters
        '''
        username = self.cleaned_data['username']
        if '.' in username:
            raise forms.ValidationError("Usernames cannot contain a full stop")
        return username

    def save(self, request):
        '''
        save the new user
        '''
        user = super(MyCustomSignupForm, self).save(request)
        return user