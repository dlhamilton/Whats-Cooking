from django import forms
from cloudinary.forms import CloudinaryInput
from cloudinary.models import CloudinaryField
from django.contrib.auth.models import User
from .models import Comments, Ingredients, Recipes, RecipeItems, Units, Methods, UserDetails, StarRating


class CommentsForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ('body',)


class RatingForm(forms.ModelForm):
    class Meta:
        model = StarRating
        fields = ('rating',)
        widgets = {
                    'rating': forms.HiddenInput(attrs={'class': 'd-none'}),
        }


class RecipesForm(forms.ModelForm):
    publish = forms.BooleanField(initial=False, required=False, widget=forms.CheckboxInput(attrs={'label': 'Publish'}))
    
    recipe_image = CloudinaryField('image')
    
    class Meta:
        model = Recipes
        fields = ('title',
                  'recipe_image',
                  'excerpt',
                  'prep_time',
                  'cook_time',
                  'serves',)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.status == 1:
            self.fields['publish'].initial = True


class SearchRecipeForm(forms.Form):
    search_query = forms.CharField(max_length=100, required=False,
    widget = forms.TextInput(attrs={'id':'search_query',
    'placeholder': 'Search...' , 'class': 'form-control'}))


class FilterRecipeForm(forms.Form):
    filter_query = forms.ModelMultipleChoiceField(
        queryset=Ingredients.objects.filter(approved=True).order_by('name'),
        widget=forms.CheckboxSelectMultiple

    )


class AddToRecipeForm(forms.Form):
    search_term = forms.CharField(required=False)
    # filter_query = forms.ModelMultipleChoiceField(
    #     queryset=Ingredients.objects.filter(approved=True).order_by('name'),
    #     widget=forms.CheckboxSelectMultiple
    # )


class RecipeItemsForm(forms.ModelForm):
    class Meta:
        model = RecipeItems
        fields = ['ingredients', 'amount', 'unit']
        widgets = {
        'ingredients': forms.TextInput(attrs={'id': 'recipient-name'}),
        }

    unit = forms.ModelChoiceField(queryset=Units.objects.all())
   
    def __init__(self, *args, **kwargs):
        super(RecipeItemsForm, self).__init__(*args, **kwargs)
        self.fields['unit'].empty_label = "Select Unit"
        self.fields['ingredients'].widget.attrs.update({'id': 'ingredient-name'})


class MethodsForm(forms.ModelForm):
    class Meta:
        model = Methods
        fields = ('method',)
        widgets = {
            'method': forms.Textarea(attrs={'rows': 4, 'class': 'method-class-design'})
        }


class UserDetailsForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    location = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    # user_image = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    user_image = CloudinaryField('image')

    class Meta:
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
    follow = forms.IntegerField(widget=forms.HiddenInput(attrs={'class': 'd-none'}),required=False)


class UnfollowForm(forms.Form):
    unfollow = forms.IntegerField(widget=forms.HiddenInput(attrs={'class': 'd-none'}),required=False)
